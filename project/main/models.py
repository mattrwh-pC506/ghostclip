from django.db import models
from django.contrib.auth.models import User, AbstractUser

class Family(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "families"

    def __str__(self):
        return self.name

class User(AbstractUser):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True)

class Item(models.Model):
    item_id = models.CharField(max_length=255, primary_key=True)
    institution_id = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    public_token = models.CharField(max_length=255)

    class Meta:
        unique_together = ('institution_id', 'family',)

    def __str__(self):
        return '{}-{}'.format(self.institution_name, self.family.name)

class Calendar(models.Model):
    calendar_id = models.CharField(max_length=255, primary_key=True)
    provider = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255)

    def __str__(self):
        return '{}-{}-{}'.format(self.provider, self.user.username, self.calendar_id)

class Account(models.Model):
    account_id = models.CharField(max_length=255, primary_key=True)
    available_balance = models.DecimalField(max_digits=20, decimal_places=2)
    current_balance = models.DecimalField(max_digits=20, decimal_places=2)
    limit = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    mask = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=100, null=True)
    official_name = models.CharField(max_length=100, null=True)
    subtype = models.CharField(max_length=50, null=True)
    type = models.CharField(max_length=50, null=True)

class Category(models.Model):
    token = models.CharField(max_length=100, primary_key=True)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)

class Location(models.Model):
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=20)
    lat = models.CharField(max_length=50)
    lon = models.CharField(max_length=50)

    class Meta:
        unique_together = ('address', 'city', 'state', 'zip', 'lon', 'lat',)

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=255, primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    categories = models.ManyToManyField(Category)
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pending = models.BooleanField()
