from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Transaction, Product
@receiver(pre_save, sender=Transaction)
def remember_old(sender, instance: Transaction, **kwargs):
    if instance.pk:
        try:
            old=sender.objects.get(pk=instance.pk)
            instance._old_qty=old.quantity
            instance._old_type=old.trx_type
        except sender.DoesNotExist:
            instance._old_qty=None; instance._old_type=None
    else:
        instance._old_qty=None; instance._old_type=None
def _apply_delta(product: Product, delta):
    product.qty_on_hand=(product.qty_on_hand or 0)+delta
    product.save(update_fields=['qty_on_hand','updated_at'])
@receiver(post_save, sender=Transaction)
def on_trx_saved(sender, instance: Transaction, created, **kwargs):
    new_delta=instance.quantity if instance.trx_type==Transaction.IN else -instance.quantity
    old_delta=0
    if getattr(instance,'_old_qty',None) is not None and getattr(instance,'_old_type',None) is not None:
        old_delta=instance._old_qty if instance._old_type==Transaction.IN else -instance._old_qty
    delta=new_delta - old_delta
    if delta: _apply_delta(instance.product, delta)
@receiver(post_delete, sender=Transaction)
def on_trx_deleted(sender, instance: Transaction, **kwargs):
    delta=-(instance.quantity) if instance.trx_type==Transaction.IN else instance.quantity
    _apply_delta(instance.product, delta)
