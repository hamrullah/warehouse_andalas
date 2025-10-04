from django.urls import path
from . import views_master as v
from .views_report import InventorySummaryView
app_name='inventory'
urlpatterns=[
 path('products/', v.ProductList.as_view(), name='product-list'),
 path('products/new/', v.ProductCreate.as_view(), name='product-create'),
 path('products/<int:pk>/edit/', v.ProductUpdate.as_view(), name='product-update'),
 path('products/<int:pk>/delete/', v.ProductDelete.as_view(), name='product-delete'),
 path('categories/', v.CategoryList.as_view(), name='category-list'),
 path('categories/new/', v.CategoryCreate.as_view(), name='category-create'),
 path('categories/<int:pk>/edit/', v.CategoryUpdate.as_view(), name='category-update'),
 path('categories/<int:pk>/delete/', v.CategoryDelete.as_view(), name='category-delete'),
 path('uoms/', v.UoMList.as_view(), name='uom-list'),
 path('uoms/new/', v.UoMCreate.as_view(), name='uom-create'),
 path('uoms/<int:pk>/edit/', v.UoMUpdate.as_view(), name='uom-update'),
 path('uoms/<int:pk>/delete/', v.UoMDelete.as_view(), name='uom-delete'),
 path('transactions/', v.TransactionList.as_view(), name='transaction-list'),
 path('transactions/new/', v.TransactionCreate.as_view(), name='transaction-create'),
 path('transactions/<int:pk>/edit/', v.TransactionUpdate.as_view(), name='transaction-update'),
 path('transactions/<int:pk>/delete/', v.TransactionDelete.as_view(), name='transaction-delete'),
 path("summary/", InventorySummaryView.as_view(), name="summary"),
]
