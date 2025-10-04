from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
class TimeStampedModel(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: abstract=True
class Category(TimeStampedModel):
    name=models.CharField(max_length=100, unique=True)
    is_active=models.BooleanField(default=True)
    def __str__(self): return self.name
class UoM(TimeStampedModel):
    name=models.CharField('Satuan', max_length=50, unique=True)
    def __str__(self): return self.name
class Product(TimeStampedModel):
    sku=models.CharField(max_length=50, unique=True)
    name=models.CharField(max_length=200)
    category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name='products')
    uom=models.ForeignKey(UoM,on_delete=models.PROTECT)
    min_stock=models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active=models.BooleanField(default=True)
    qty_on_hand=models.DecimalField(max_digits=12, decimal_places=2, default=0)
    class Meta: ordering=['name']
    def __str__(self): return f"{self.sku} - {self.name}"
class Transaction(TimeStampedModel):
    IN, OUT='IN','OUT'
    TYPE_CHOICES=[(IN,'Masuk'),(OUT,'Keluar')]
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='transactions')
    trx_type=models.CharField(max_length=3, choices=TYPE_CHOICES)
    quantity=models.DecimalField(max_digits=12, decimal_places=2)
    note=models.CharField(max_length=255, blank=True)
    trx_date=models.DateTimeField(default=timezone.now)
    class Meta: ordering=['-trx_date','-id']
    def clean(self):
        if self.quantity<=0: raise ValidationError('Quantity harus > 0')
        current=self.product.qty_on_hand
        if self.pk:
            try:
                old=Transaction.objects.get(pk=self.pk)
                old_delta=old.quantity if old.trx_type==self.IN else -old.quantity
                current=current - old_delta
            except Transaction.DoesNotExist:
                pass
        delta=self.quantity if self.trx_type==self.IN else -self.quantity
        if current + delta < 0:
            raise ValidationError('Stok tidak cukup untuk transaksi keluar.')
    def __str__(self):
        sign='+' if self.trx_type==self.IN else '-'
        return f"{self.trx_date:%Y-%m-%d} {sign}{self.quantity} {self.product}"
