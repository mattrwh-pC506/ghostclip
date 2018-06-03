from django.db import models
from main.models.rules import RuleSet
from main.models.item import Item


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
        RuleSet, null=True, on_delete=models.SET_NULL)
