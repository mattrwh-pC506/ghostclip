from django.db import models
from django.contrib.auth.models import User, AbstractUser

class Family(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "families"

    def __str__(self):
        return self.name

class User(AbstractUser):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)

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

class Calendar(models.Model):
    calendar_id = models.CharField(max_length=255, primary_key=True)
    provider = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255)

    def __str__(self):
        return '{}-{}-{}'.format(self.provider, self.user.username, self.calendar_id)

class Account(models.Model):
    account_id = models.CharField(max_length=255, primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    available_balance = models.DecimalField(max_digits=20, decimal_places=2)
    current_balance = models.DecimalField(max_digits=20, decimal_places=2)
    limit = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    mask = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=100, null=True)
    official_name = models.CharField(max_length=100, null=True)
    subtype = models.CharField(max_length=50, null=True)
    type = models.CharField(max_length=50, null=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.mask, self.name, self.subtype)

class Category(models.Model):
    token = models.CharField(max_length=100, primary_key=True)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)

class Location(models.Model):
    address = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=20, null=True)
    zip = models.CharField(max_length=20, null=True)
    lat = models.CharField(max_length=50, null=True)
    lon = models.CharField(max_length=50, null=True)

    class Meta:
        unique_together = ('address', 'city', 'state', 'zip', 'lon', 'lat',)

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=255, primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    categories = models.ManyToManyField(Category, null=True)
    date = models.DateField(null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    pending = models.BooleanField()
