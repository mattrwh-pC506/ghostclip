from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    item_id = models.CharField(max_length=255, primary_key=True)
    institution_id = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)

    class Meta:
        unique_together = ('institution_id', 'user',)


class Calendar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
