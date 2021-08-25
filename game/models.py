from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.deletion.CASCADE)


class Zone(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)


class DeckType(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)


class Deck(models.Model):
    type = models.OneToOneField(DeckType, on_delete=models.deletion.CASCADE)


class Game(models.Model):
    players = models.ManyToManyField(Player)
    zones = models.ManyToManyField(Zone)
