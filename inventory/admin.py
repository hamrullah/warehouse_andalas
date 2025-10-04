from django.contrib import admin
from .models import Category, UoM, Product, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name','is_active','created_at')
    list_filter=('is_active',)
@admin.register(UoM)
class UoMAdmin(admin.ModelAdmin):
    list_display=('name','created_at')
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=('sku','name','category','uom','qty_on_hand','min_stock','is_active')
    search_fields=('sku','name')
    list_filter=('category','is_active')
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display=('trx_date','product','trx_type','quantity','note')
    list_filter=('trx_type','product')
    date_hierarchy='trx_date'
