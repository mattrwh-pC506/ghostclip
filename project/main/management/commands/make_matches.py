import datetime
from django.core.management.base import BaseCommand
from main.models import Transaction
from main.projector import add_to_matching_rule_set_if_any


class Command(BaseCommand):
    help = 'Generate matches and tie to rulesets'

    def add_arguments(self, parser):
        parser.add_argument('--from', help='From date in range')
        parser.add_argument('--to', help='To date in range')

    def handle(self, *args, **options):
        _from = datetime.datetime.strptime(
            options['from'] or '2016-01-01', '%Y-%m-%d')
        _to = datetime.datetime.strptime(
            options['to'] or '3000-01-01', '%Y-%m-%d')
        for transaction in Transaction.objects.filter(date__range=(_from, _to)):
            add_to_matching_rule_set_if_any(transaction)
