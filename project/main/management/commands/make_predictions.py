from collections import defaultdict
from dateutil import relativedelta
from statistics import mean
from django.core.management.base import BaseCommand, CommandError
from main.models import Transaction


def calculate_next_date(transactions, last_transaction):
    avg_day = round(mean(t.date.day for t in transactions))
    next_transaction_date = last_transaction.date + \
        relativedelta.relativedelta(months=+1)
    next_transaction_date.replace(day=avg_day)
    return next_transaction_date


class Command(BaseCommand):
    help = 'Uses existing matches to predict when next transaction will hit'

    def handle(self, *args, **options):
        rule_sets = defaultdict(list)
        for transaction in Transaction.objects.exclude(rule_set__isnull=True).order_by('-date'):
            rule_sets[transaction.rule_set].append(transaction)

        for rs, transactions in rule_sets.items():
            last_transaction = transactions[0]
            rs.predicted_next_transaction_date = calculate_next_date(
                transactions, last_transaction)
            rs.last_transaction_name = last_transaction.name
            rs.last_transaction_amount = last_transaction.amount
            rs.save()
