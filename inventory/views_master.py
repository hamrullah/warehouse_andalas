from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Product, Category, UoM, Transaction
from .forms import ProductForm, CategoryForm, UoMForm, TransactionForm
from django.db.models import Q, F
class ProductList(LoginRequiredMixin, ListView):
    model = Product
    template_name = "inventory/product_list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("category", "uom")
        q = (self.request.GET.get("q") or "").strip()
        cat = self.request.GET.get("cat") or ""
        active = self.request.GET.get("active") or ""
        low = self.request.GET.get("low") or ""  # "1" artinya hanya low stock

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
        if cat:
            qs = qs.filter(category_id=cat)
        if active in ("1", "0"):
            qs = qs.filter(is_active=(active == "1"))
        if low == "1":
            qs = qs.filter(qty_on_hand__lt=F("min_stock"))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.order_by("name")
        # preserve nilai filter biar form tetap terisi
        ctx["flt_q"] = self.request.GET.get("q", "")
        ctx["flt_cat"] = self.request.GET.get("cat", "")
        ctx["flt_active"] = self.request.GET.get("active", "")
        ctx["flt_low"] = self.request.GET.get("low", "")
        return ctx
class ProductCreate(LoginRequiredMixin, CreateView):
    model, form_class, success_url = Product, ProductForm, reverse_lazy('inventory:product-list')
class ProductUpdate(LoginRequiredMixin, UpdateView):
    model, form_class, success_url = Product, ProductForm, reverse_lazy('inventory:product-list')
class ProductDelete(LoginRequiredMixin, DeleteView):
    model, success_url = Product, reverse_lazy('inventory:product-list')
class CategoryList(LoginRequiredMixin, ListView): model=Category
class CategoryCreate(LoginRequiredMixin, CreateView):
    model, form_class, success_url = Category, CategoryForm, reverse_lazy('inventory:category-list')
class CategoryUpdate(LoginRequiredMixin, UpdateView):
    model, form_class, success_url = Category, CategoryForm, reverse_lazy('inventory:category-list')
class CategoryDelete(LoginRequiredMixin, DeleteView):
    model, success_url = Category, reverse_lazy('inventory:category-list')
class UoMList(LoginRequiredMixin, ListView): model=UoM
class UoMCreate(LoginRequiredMixin, CreateView):
    model = UoM
    form_class = UoMForm
    template_name = "inventory/uom/uom_form.html"   # taruh nanti di templates/inventory/uom/uom_form.html
    success_url = reverse_lazy("inventory:uom-list")


class UoMUpdate(LoginRequiredMixin, UpdateView):
    model = UoM
    form_class = UoMForm
    template_name = "inventory/uom/uom_form.html"
    success_url = reverse_lazy("inventory:uom-list")


class UoMDelete(LoginRequiredMixin, DeleteView):
    model = UoM
    template_name = "inventory/uom/uom_confirm_delete.html"  # taruh di templates/inventory/uom/uom_confirm_delete.html
    success_url = reverse_lazy("inventory:uom-list")
    
class TransactionList(LoginRequiredMixin, ListView): model=Transaction
class TransactionCreate(LoginRequiredMixin, CreateView):
    model, form_class, success_url = Transaction, TransactionForm, reverse_lazy('inventory:transaction-list')
class TransactionUpdate(LoginRequiredMixin, UpdateView):
    model, form_class, success_url = Transaction, TransactionForm, reverse_lazy('inventory:transaction-list')
class TransactionDelete(LoginRequiredMixin, DeleteView):
    model, success_url = Transaction, reverse_lazy('inventory:transaction-list')
