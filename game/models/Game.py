from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.apps import apps

from cardDatabase.models import Card


class Game(models.Model):
    class Meta:
        app_label = 'game'

    players = models.ManyToManyField('Player')
    zones = models.ManyToManyField('Area')
    active = models.BooleanField(default=True, blank=False, null=False)


class GameResult(models.Model):
    class Meta:
        app_label = 'game'

    winners = models.ManyToManyField('Player', related_name="winners")
    losers = models.ManyToManyField('Player', related_name="losers")
    game = models.ForeignKey('Game', on_delete=models.CASCADE)


class GameArea(models.Model):
    class Meta:
        app_label = 'game'

    area = models.ForeignKey('Area', on_delete=models.CASCADE)
    controller = models.ForeignKey('Player', on_delete=models.CASCADE)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)


class GameCard(models.Model):
    class Meta:
        app_label = 'game'

    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    card_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=Card.get_type_choices)
    card_id = models.PositiveIntegerField()
    card = GenericForeignKey('card_type', 'card_id')
    game_area = models.ForeignKey('GameArea', on_delete=models.CASCADE)

