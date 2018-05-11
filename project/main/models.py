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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)

    class Meta:
        unique_together = ('institution_id', 'user',)

    def __str__(self):
        return '{}-{}'.format(self.institution_name, self.user.username)

class Calendar(models.Model):
    calendar_id = models.CharField(max_length=255, primary_key=True)
    provider = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255)

    def __str__(self):
        return '{}-{}-{}'.format(self.provider, self.user.username, self.user.calendar_id)
