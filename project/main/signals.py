from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction
from .calendar import (
        create_transaction_event,
        patch_transaction_event,
        delete_transaction_event)

@receiver(post_save, sender=Transaction)
def transaction_saved(sender, instance, created, **kwargs):
    if created:
        create_transaction_event(instance)
    else:
        patch_transaction_event(instance)

@receiver(post_delete, sender=Transaction)
def transaction_deleted(sender, instance, **kwargs):
    delete_transaction_event(instance)
