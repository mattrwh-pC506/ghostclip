from collections import defaultdict
from datetime import timedelta
from dateutil import relativedelta
from calendar import monthrange
from statistics import mean
from django.core.management.base import BaseCommand, CommandError
from main.models import Transaction
from main.gacalendar.rule_sets import (
    create_rule_set_event,
    patch_rule_set_event,
    delete_rule_set_event)

import django_rq


def closest_weekday_date(date_to_check, weekday):
    return [d for d in[date_to_check+timedelta(o-3) for o in range(7)] if weekday % 7 == d.weekday()][0]


def calculate_next_date(transactions, last_transaction):
    date_to_check = last_transaction.date
    rule_set = last_transaction.rule_set
    date_rule = rule_set.date_rule_info
    next_transaction_date = None

    if date_rule.repeats_every_type == 'MONTH':
        most_common_day = rule_set.most_common_day() or last_transaction.date.day
        next_transaction_date = date_to_check + \
            relativedelta.relativedelta(months=+date_rule.repeats_every_num)
        days_in_month = monthrange(
            next_transaction_date.year, next_transaction_date.month)[1]
        if most_common_day > days_in_month:
            most_common_day = days_in_month
        next_transaction_date.replace(day=most_common_day)
        weekday = next_transaction_date.weekday()
        if weekday > 4 and weekday <= 6:
            days_to_add = 7 - weekday
            next_transaction_date = next_transaction_date + \
                relativedelta.relativedelta(days=+days_to_add)
    elif date_rule.repeats_every_type == 'DAY':
        next_transaction_date = date_to_check + \
            relativedelta.relativedelta(days=+date_rule.repeats_every_num)

        if ((date_rule.repeats_every_num % 7) == 0):
            most_common_weekday = rule_set.most_common_day_of_week()
            next_transaction_date = closest_weekday_date(
                next_transaction_date, most_common_weekday)

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

            if rs.calendar_event_id:
                django_rq.enqueue(patch_rule_set_event, rs)
            elif Transaction.objects.filter(rule_set=rs):
                django_rq.enqueue(create_rule_set_event, rs)
