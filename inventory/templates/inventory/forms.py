# inventory/forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Div
from .models import Product, Category, UoM, Transaction

class BaseCrispyModelForm(forms.ModelForm):
    """Form dasar agar semua punya helper crispy secara konsisten."""
    def _init_helper(self):
        self.helper = FormHelper()
        self.helper.form_method = "post"
        # biarkan tombol submit di template partial (_form.html), jadi tidak perlu Submit() di sini
        self.helper.label_class = "form-label"
        # Bootstrap 5 tidak butuh field_class khusus, pakai grid via Row/Column saja
        self.helper.field_class = ""

class ProductForm(BaseCrispyModelForm):
    class Meta:
        model = Product
        fields = ["sku", "name", "category", "uom", "min_stock", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_helper()
        self.helper.layout = Layout(
            Row(
                Column(Field("sku"), css_class="col-md-4"),
                Column(Field("name"), css_class="col-md-8"),
            ),
            Row(
                Column(Field("category"), css_class="col-md-6"),
                Column(Field("uom"), css_class="col-md-6"),
            ),
            Row(
                Column(Field("min_stock"), css_class="col-md-4"),
                Column(Field("is_active"), css_class="col-md-4 align-self-end"),
            ),
            HTML("""
            <div class="alert alert-info mt-3" role="alert">
              Stok aktual (<code>qty_on_hand</code>) berubah otomatis dari Transaksi IN/OUT.
            </div>
            """)
        )

class CategoryForm(BaseCrispyModelForm):
    class Meta:
        model = Category
        fields = ["name", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_helper()
        self.helper.layout = Layout(
            Row(
                Column(Field("name"), css_class="col-md-8"),
                Column(Field("is_active"), css_class="col-md-4 align-self-end"),
            )
        )

class UoMForm(BaseCrispyModelForm):
    class Meta:
        model = UoM
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_helper()
        self.helper.layout = Layout(
            Row(
                Column(Field("name"), css_class="col-md-6"),
            )
        )

class TransactionForm(BaseCrispyModelForm):
    class Meta:
        model = Transaction
        fields = ["product", "trx_type", "quantity", "note", "trx_date"]
        widgets = {
            # gunakan input datetime-local agar enak dipakai
            "trx_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "note": forms.TextInput(attrs={"placeholder": "Catatan opsional"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_helper()

        # Jika initial trx_date ada (objek edit), format ulang ke HTML5 datetime-local (YYYY-MM-DDTHH:MM)
        if self.initial.get("trx_date") and hasattr(self.initial["trx_date"], "strftime"):
            self.initial["trx_date"] = self.initial["trx_date"].strftime("%Y-%m-%dT%H:%M")

        self.helper.layout = Layout(
            Row(
                Column(Field("product"), css_class="col-md-6"),
                Column(Field("trx_type"), css_class="col-md-3"),
                Column(Field("quantity"), css_class="col-md-3"),
            ),
            Row(
                Column(Field("trx_date"), css_class="col-md-4"),
                Column(Field("note"), css_class="col-md-8"),
            ),
            HTML("""
            <div class="alert alert-secondary mt-3" role="alert">
              <strong>Catatan:</strong> Transaksi <em>Masuk</em> menambah, <em>Keluar</em> mengurangi stok.
              Sistem mencegah stok negatif secara otomatis.
            </div>
            """)
        )
