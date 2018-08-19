from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from main.models import Transaction, RunningTotal
from main.gacalendar.transactions import (
    create_transaction_event,
    patch_transaction_event,
    delete_transaction_event)
from main.matcher import add_to_matching_rule_set_if_any

from main.gacalendar.running_totals import create_running_total_event, patch_running_total_event
from main.running_totaler import create_or_update_running_total_from_transaction

import django_rq


@receiver(post_save, sender=Transaction)
def transaction_saved(sender, instance, created, **kwargs):
    if created:
        if instance.calendar_event_id:
            django_rq.enqueue(patch_transaction_event, instance)
        else:
            django_rq.enqueue(create_transaction_event, instance)
    else:
        django_rq.enqueue(patch_transaction_event, instance)

    django_rq.enqueue(add_to_matching_rule_set_if_any, instance)
    django_rq.enqueue(
        create_or_update_running_total_from_transaction, instance)


@receiver(post_delete, sender=Transaction)
def transaction_deleted(sender, instance, **kwargs):
    django_rq.enqueue(delete_transaction_event, instance)


@receiver(post_save, sender=RunningTotal)
def running_total_saved(sender, instance, created, **kwargs):
    if created:
        if instance.calendar_event_id:
            django_rq.enqueue(patch_running_total_event, instance)
        else:
            django_rq.enqueue(create_running_total_event, instance)
    else:
        django_rq.enqueue(patch_running_total_event, instance)
