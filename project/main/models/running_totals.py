from django.db import models
from main.models import Account


class RunningTotal(models.Model):
    calendar_event_id = models.CharField(max_length=255, null=True, blank=True)
    target = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
