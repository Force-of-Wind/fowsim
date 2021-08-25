from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
