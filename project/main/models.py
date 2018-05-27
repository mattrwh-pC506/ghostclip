from django.db import models
from django.contrib.auth.models import User, AbstractUser


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
    operator = models.CharField(max_length=20, choices=(
        ('CONTAINS', 'contains (case sensitive)'),
        ('EXACT', 'exact (case sensitive)'),
        ('STARTSWITH', 'startswith (case sensitive)'),
        ('ENDSWITH', 'endswith (case sensitive)'),
    ))
    value = models.CharField(max_length=255)

    matchers = {
        'CONTAINS': lambda name, value: name in value,
        'EXACT': lambda name, value: name == value,
        'STARTSWITH': lambda name, value: value.startsWith(name),
        'ENDSWITH': lambda name, value: value.endsWith(name),
    }

    def matches(self, transaction_name):
        value = self.value.lower()
        name = transaction_name.lower()
        return matchers.get(self.operator, lambda: False)(name, value)


class AmountRule(models.Model):
    rule_set = models.ForeignKey(RuleSet, on_delete=models.CASCADE)
    operator = models.CharField(max_length=20, choices=(
        ('EQ', '='),
        ('GT', '>'),
        ('GTE', '≥'),
        ('LT', '<'),
        ('LTE', '≤'),
    ))
    value = models.IntegerField()

    matchers = {
        'EQ': lambda amount, value: amount == value,
        'GT': lambda amount, value: amount > value,
        'GTE': lambda amount, value: amount >= value,
        'LT': lambda amount, value: amount < value,
        'LTE': lambda amount, value: amount <= value,
    }

    def matches(self, amount):
        return matchers.get(self.operator, lambda: False)(amount, self.value)


class DateRule(models.Model):
    rule_set = models.ForeignKey(RuleSet, on_delete=models.CASCADE)
    repeats_every_num = models.IntegerField(default=1)
    repeats_every_type = models.CharField(max_length=20, choices=(
        ('DAY', 'day'),
        ('WEEK', 'week'),
        ('MONTH', 'month'),
    ))
    day_of_week = models.IntegerField(null=True, blank=True, choices=(
        (1, 'Sunday'),
        (2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
        (7, 'Saturday'),
    ))
    day_of_month = models.IntegerField(null=True, blank=True)
