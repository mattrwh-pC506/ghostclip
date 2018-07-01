from django.db import models
from dateutil import relativedelta
import datetime
from statistics import mode, StatisticsError
from main.models.item import Item


class RuleSet(models.Model):
    name = models.CharField(max_length=100)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    last_transaction_name = models.TextField(null=True, blank=True)
    last_transaction_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    predicted_next_transaction_date = models.DateField(null=True, blank=True)
    calendar_event_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    def most_common_day(self):
        ts = self.transactions.all()
        if ts:
            try:
                return mode(t.date.day for t in ts)
            except StatisticsError:
                pass

    def most_common_day_of_week(self):
        ts = self.transactions.all()
        if ts:
            try:
                return mode(t.date.weekday() for t in ts)
            except StatisticsError:
                pass


class NameRule(models.Model):
    rule_set = models.ForeignKey(RuleSet, on_delete=models.CASCADE)
    OPERATOR_CHOICES = (
        ('CONTAINS', 'contains (case isensitive)'),
        ('EXACT', 'exact (case isensitive)'),
        ('STARTSWITH', 'startswith (case isensitive)'),
        ('ENDSWITH', 'endswith (case isensitive)'),
    )
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES)
    value = models.CharField(max_length=255)

    matchers = {
        'CONTAINS': lambda name, value: value in name,
        'EXACT': lambda name, value: value == name,
        'STARTSWITH': lambda name, value: name.startswith(value),
        'ENDSWITH': lambda name, value: name.endswith(value),
    }

    def matches(self, transaction_name):
        name = transaction_name.lower()
        value = self.value.lower()
        matcher_predicate = self.matchers.get(
            self.operator, lambda x, y: False)
        return matcher_predicate(name, value)


class AmountRule(models.Model):
    rule_set = models.ForeignKey(RuleSet, on_delete=models.CASCADE)

    OPERATOR_CHOICES = (
        ('EQ', '='),
        ('GT', '>'),
        ('GTE', '≥'),
        ('LT', '<'),
        ('LTE', '≤'),
    )
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES)

    TRANSACTION_TYPE_CHOICES = (
        ('LOAD', 'load'),
        ('DEBIT', 'debit'),
    )
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='DEBIT')

    value = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)

    matchers = {
        'EQ': lambda amount, value: amount == value,
        'GT': lambda amount, value: amount > value,
        'GTE': lambda amount, value: amount >= value,
        'LT': lambda amount, value: amount < value,
        'LTE': lambda amount, value: amount <= value,
    }

    def matches(self, transaction_amount):
        if self.transaction_type == 'DEBIT' and transaction_amount > 0:
            return False

        if self.transaction_type == 'LOAD' and transaction_amount < 0:
            return False

        matcher_predicate = self.matchers.get(
            self.operator, lambda x, y: False)
        return matcher_predicate(abs(transaction_amount), abs(self.value))


class DateRule(models.Model):
    rule_set = models.OneToOneField(
        RuleSet, on_delete=models.CASCADE, related_name='date_rule_info')
    repeats_every_num = models.IntegerField(default=1)
    starting_date = models.DateField()
    day_range_buffer = models.IntegerField(default=0)
    TYPE_CHOICES = (
        ('DAY', 'day'),
        ('MONTH', 'month'),
    )
    repeats_every_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def within_days_buffer(self, days_from_last, days_to_next):
        return days_from_last <= self.day_range_buffer or days_to_next <= self.day_range_buffer

    def match_repeating_day(self, transaction_date):
        delta = transaction_date - self.starting_date
        days_from_last = delta.days % self.repeats_every_num
        days_to_next = self.repeats_every_num - days_from_last
        return self.within_days_buffer(days_from_last, days_to_next)

    def match_repeating_month(self, transaction_date):
        delta = relativedelta.relativedelta(
            transaction_date, self.starting_date)
        months_from_last = delta.months % self.repeats_every_num
        months_to_next = self.repeats_every_num - months_from_last
        within_buffer_range = False
        last_repetition = transaction_date - \
            datetime.timedelta(days=delta.days)
        next_repetition = last_repetition + \
            relativedelta.relativedelta(months=+1)

        last_rep_days_ago = (
            transaction_date - last_repetition).days
        next_repetition_days_from_now = (
            next_repetition - transaction_date).days
        if (months_from_last <= 1):
            if last_rep_days_ago < next_repetition_days_from_now:
                within_buffer_range = last_rep_days_ago <= self.day_range_buffer
            elif last_rep_days_ago >= next_repetition_days_from_now:
                within_buffer_range = next_repetition_days_from_now <= self.day_range_buffer
        elif ((not within_buffer_range) and months_to_next <= 1):
            days_to_next = next_repetition - transaction_date
            within_buffer_range = days_to_next.days <= self.day_range_buffer
        return within_buffer_range

    def matches(self, transaction_date):
        if (self.repeats_every_type == 'DAY'):
            return self.match_repeating_day(transaction_date)
        elif (self.repeats_every_type == 'MONTH'):
            return self.match_repeating_month(transaction_date)
        else:
            return False
