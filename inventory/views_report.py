# inventory/views_report.py
from datetime import datetime, timedelta
import csv
from io import StringIO

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F, Sum, Value, DecimalField, Count
from django.db.models.functions import Coalesce, TruncDate
from django.utils.dateparse import parse_date, parse_datetime
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.http import urlencode

from .models import Transaction, Product, Category


class InventorySummaryView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/summary.html"

    # ------------- helpers -------------
    def _parse_any_datetime(self, s: str | None):
        if not s:
            return None
        return parse_datetime(s) or (
            parse_date(s) and datetime.combine(parse_date(s), datetime.min.time())
        )

    def _filtered_trx_qs(self):
        """
        Return: (qs, start_raw, end_raw, start_dt, end_dt, cat_id, prod_id)
        Filter by date + (optional) category id (cat) & product id (prod).
        """
        request = self.request
        start_raw = request.GET.get("start") or ""
        end_raw = request.GET.get("end") or ""
        cat_id = request.GET.get("cat") or ""
        prod_id = request.GET.get("prod") or ""

        start_dt = self._parse_any_datetime(start_raw) if start_raw else None
        end_dt = self._parse_any_datetime(end_raw) if end_raw else None
        if end_dt and ("T" not in end_raw):
            end_dt = end_dt + timedelta(days=1)

        qs = Transaction.objects.select_related("product", "product__category", "product__uom")
        if start_dt:
            qs = qs.filter(trx_date__gte=start_dt)
        if end_dt:
            qs = qs.filter(trx_date__lt=end_dt)
        if cat_id:
            qs = qs.filter(product__category_id=cat_id)
        if prod_id:
            qs = qs.filter(product_id=prod_id)

        return qs, start_raw, end_raw, start_dt, end_dt, cat_id, prod_id

    # ------------- GET (export handling) -------------
    def get(self, request, *args, **kwargs):
        export = request.GET.get("export")
        kind = request.GET.get("kind", "summary")  # "summary" | "detail"
        trx_qs, start_raw, end_raw, start_dt, end_dt, cat_id, prod_id = self._filtered_trx_qs()

        if export == "csv":
            if kind == "detail":
                return self._export_csv_detail(trx_qs)
            return self._export_csv_summary(trx_qs, start_dt, end_dt, cat_id, prod_id)

        return super().get(request, *args, **kwargs)

    # ------------- context -------------
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        trx_qs, start_raw, end_raw, start_dt, end_dt, cat_id, prod_id = self._filtered_trx_qs()

        # KPI total
        total_in = trx_qs.aggregate(s=Sum("quantity", filter=Q(trx_type="IN")))["s"] or 0
        total_out = trx_qs.aggregate(s=Sum("quantity", filter=Q(trx_type="OUT")))["s"] or 0

        # Produk dasar untuk rekap per-produk (terapkan filter cat/prod di sini)
        product_base = Product.objects.all()
        if cat_id:
            product_base = product_base.filter(category_id=cat_id)
        if prod_id:
            product_base = product_base.filter(id=prod_id)

        # Low stock (global, tidak ikut filter tanggal—sesuai makna "low stock" saat ini)
        count_low_stock = Product.objects.filter(qty_on_hand__lt=F("min_stock"), is_active=True).count()

        # filter tanggal untuk annotate transaksi
        date_filter = Q()
        if start_dt:
            date_filter &= Q(transactions__trx_date__gte=start_dt)
        if end_dt:
            date_filter &= Q(transactions__trx_date__lt=end_dt)

        per_product = (
            product_base
            .annotate(
                in_qty=Coalesce(
                    Sum("transactions__quantity",
                        filter=Q(transactions__trx_type="IN") & date_filter),
                    Value(0), output_field=DecimalField(max_digits=12, decimal_places=2)
                ),
                out_qty=Coalesce(
                    Sum("transactions__quantity",
                        filter=Q(transactions__trx_type="OUT") & date_filter),
                    Value(0), output_field=DecimalField(max_digits=12, decimal_places=2)
                ),
            )
            .annotate(net=F("in_qty") - F("out_qty"))
            .order_by("name")
        )

        # timeseries untuk chart (pakai trx_qs yang sudah semua filter)
        per_day = (
            trx_qs
            .annotate(d=TruncDate("trx_date"))
            .values("d", "trx_type")
            .annotate(q=Sum("quantity"))
            .order_by("d")
        )
        labels, in_map, out_map = [], {}, {}
        for row in per_day:
            d = row["d"]
            if d not in labels:
                labels.append(d)
            if row["trx_type"] == "IN":
                in_map[d] = row["q"] or 0
            else:
                out_map[d] = row["q"] or 0
        chart_labels = [d.strftime("%Y-%m-%d") for d in labels]
        chart_in = [in_map.get(d, 0) for d in labels]
        chart_out = [out_map.get(d, 0) for d in labels]

        # pilihan dropdown
        categories = Category.objects.order_by("name")
        products = Product.objects.order_by("name")
        # urls export (bawa filter)
        query_base = {}
        if start_raw:
            query_base["start"] = start_raw
        if end_raw:
            query_base["end"] = end_raw
        if cat_id:
            query_base["cat"] = cat_id
        if prod_id:
            query_base["prod"] = prod_id

        summary_url = f"?{urlencode({**query_base, 'export':'csv', 'kind':'summary'})}" if query_base else "?export=csv&kind=summary"
        detail_url = f"?{urlencode({**query_base, 'export':'csv', 'kind':'detail'})}" if query_base else "?export=csv&kind=detail"

        ctx.update({
            "filter_start": start_raw,
            "filter_end": end_raw,
            "filter_cat": cat_id,
            "filter_prod": prod_id,

            "total_in": total_in,
            "total_out": total_out,
            "count_low_stock": count_low_stock,

            "per_product": per_product,

            "chart_labels": chart_labels,
            "chart_in": chart_in,
            "chart_out": chart_out,

            "categories": categories,
            "products": products,

            "export_csv_url": summary_url,
            "export_csv_detail_url": detail_url,
        })
        return ctx

    # ------------- CSV exports -------------
    def _export_csv_summary(self, trx_qs, start_dt, end_dt, cat_id, prod_id):
        product_base = Product.objects.all()
        if cat_id:
            product_base = product_base.filter(category_id=cat_id)
        if prod_id:
            product_base = product_base.filter(id=prod_id)

        date_filter = Q()
        if start_dt:
            date_filter &= Q(transactions__trx_date__gte=start_dt)
        if end_dt:
            date_filter &= Q(transactions__trx_date__lt=end_dt)

        per_product = (
            product_base
            .annotate(
                in_qty=Coalesce(Sum("transactions__quantity",
                                    filter=Q(transactions__trx_type="IN") & date_filter),
                                Value(0), output_field=DecimalField(max_digits=12, decimal_places=2)),
                out_qty=Coalesce(Sum("transactions__quantity",
                                     filter=Q(transactions__trx_type="OUT") & date_filter),
                                 Value(0), output_field=DecimalField(max_digits=12, decimal_places=2)),
            )
            .annotate(net=F("in_qty") - F("out_qty"))
            .order_by("name")
        )

        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(["SKU", "Nama", "Kategori", "Satuan", "Masuk", "Keluar", "Net", "On Hand", "Min"])
        for p in per_product:
            w.writerow([p.sku, p.name, str(p.category), str(p.uom), p.in_qty, p.out_qty, p.net, p.qty_on_hand, p.min_stock])

        resp = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="ringkasan_stok_per_produk.csv"'
        return resp

    def _export_csv_detail(self, trx_qs):
        # detail semua baris transaksi sesuai filter aktif
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(["Tanggal", "SKU", "Produk", "Kategori", "Satuan", "Tipe", "Qty", "Catatan"])
        for t in trx_qs.order_by("trx_date", "id"):
            p = t.product
            w.writerow([
                t.trx_date.strftime("%Y-%m-%d %H:%M:%S"),
                p.sku, p.name, str(p.category), str(p.uom),
                t.trx_type, t.quantity, t.note or ""
            ])
        resp = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="detail_transaksi_stok.csv"'
        return resp
