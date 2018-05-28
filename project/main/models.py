from django.db import models
from django.contrib.auth.models import User, AbstractUser
from dateutil import relativedelta
import datetime


class Family(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "families"

    def __str__(self):
        return self.name


class User(AbstractUser):
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, null=True, blank=True)


class Item(models.Model):
    item_id = models.CharField(max_length=255, primary_key=True)
    institution_id = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    public_token = models.CharField(max_length=255)

    class Meta:
        unique_together = ('institution_id', 'user',)

    def __str__(self):
        return '{}-{}'.format(self.institution_name, self.user.family.name)


class Account(models.Model):
    account_id = models.CharField(max_length=255, primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    available_balance = models.DecimalField(max_digits=20, decimal_places=2)
    current_balance = models.DecimalField(max_digits=20, decimal_places=2)
    limit = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    mask = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=255, null=True)
    official_name = models.CharField(max_length=255, null=True, blank=True)
    subtype = models.CharField(max_length=50, null=True)
    type = models.CharField(max_length=50, null=True)

    track = models.BooleanField()

    def __str__(self):
        return '{}-{}-{}'.format(self.mask, self.name, self.subtype)


class Category(models.Model):
    token = models.CharField(max_length=255, primary_key=True)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)


class Location(models.Model):
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=20, null=True)
    zip = models.CharField(max_length=20, null=True)
    lat = models.CharField(max_length=50, null=True)
    lon = models.CharField(max_length=50, null=True)

    class Meta:
        unique_together = ('address', 'city', 'state', 'zip', 'lon', 'lat',)


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=255, primary_key=True)
    calendar_event_id = models.CharField(max_length=255, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    categories = models.ManyToManyField(Category)
    date = models.DateField(null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    pending = models.BooleanField()
    rule_set = models.ForeignKey(
        'RuleSet', null=True, on_delete=models.SET_NULL)


class RuleSet(models.Model):
    name = models.CharField(max_length=100)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)


class NameRule(models.Model):
    rule_set = models.ForeignKey(RuleSet, on_delete=models.CASCADE)
    OPERATOR_CHOICES = (
        ('CONTAINS', 'contains (case sensitive)'),
        ('EXACT', 'exact (case sensitive)'),
        ('STARTSWITH', 'startswith (case sensitive)'),
        ('ENDSWITH', 'endswith (case sensitive)'),
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
    value = models.IntegerField()

    matchers = {
        'EQ': lambda amount, value: amount == value,
        'GT': lambda amount, value: amount > value,
        'GTE': lambda amount, value: amount >= value,
        'LT': lambda amount, value: amount < value,
        'LTE': lambda amount, value: amount <= value,
    }

    def matches(self, transaction_amount):
        matcher_predicate = self.matchers.get(
            self.operator, lambda x, y: False)
        return matcher_predicate(transaction_amount, self.value)


class DateRule(models.Model):
    rule_set = models.ForeignKey(RuleSet, on_delete=models.CASCADE)
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
