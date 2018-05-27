from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction
from .gacalendar import (
    create_transaction_event,
    patch_transaction_event,
    delete_transaction_event)
from .projector import add_to_matching_rule_set_if_any

import django_rq


@receiver(post_save, sender=Transaction)
def transaction_saved(sender, instance, created, **kwargs):
    if created:
        django_rq.enqueue(create_transaction_event, instance)
    else:
        django_rq.enqueue(patch_transaction_event, instance)

    django_rq.enqueue(add_to_matching_rule_set_if_any, instance)


@receiver(post_delete, sender=Transaction)
def transaction_deleted(sender, instance, **kwargs):
    django_rq.enqueue(delete_transaction_event, instance)
