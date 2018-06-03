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
