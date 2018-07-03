from collections import defaultdict
from datetime import timedelta
from dateutil import relativedelta
from calendar import monthrange
from main.predictor import make_predictions
from django.core.management.base import BaseCommand, CommandError
from main.models import Transaction

import django_rq


class Command(BaseCommand):
    help = 'Uses existing matches to predict when next transaction will hit'

    def handle(self, *args, **options):
        rule_set_map = defaultdict(list)
        for transaction in Transaction.objects.exclude(rule_set__isnull=True).order_by('-date'):
            rule_set_map[transaction.rule_set].append(transaction)
        make_predictions(rule_set_map)
