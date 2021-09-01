from django.db import models

from . import Player
from . import Area


class Game(models.Model):
    players = models.ManyToManyField(Player.Player)
    zones = models.ManyToManyField(Area)
    active = models.BooleanField(default=True, blank=False, null=False)


class GameResult(models.Model):
    winners = models.ManyToManyField(Player.Player, related_name="winners")
    losers = models.ManyToManyField(Player.Player, related_name="losers")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
