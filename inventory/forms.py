from django import forms
from .models import Product, Category, UoM, Transaction
class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['sku','name','category','uom','min_stock','is_active']
class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=['name','is_active']
class UoMForm(forms.ModelForm):
    class Meta:
        model=UoM
        fields=['name']
class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transaction
        fields=['product','trx_type','quantity','note','trx_date']
