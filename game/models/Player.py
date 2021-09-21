from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    class Meta:
        app_label = 'game'
    user = models.OneToOneField(User, on_delete=models.deletion.CASCADE)
