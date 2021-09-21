from django.db import models


class DeckType(models.Model):
    class Meta:
        app_label = 'game'

    name = models.CharField(max_length=200, null=False, blank=False)


class Deck(models.Model):
    class Meta:
        app_label = 'game'

    type = models.OneToOneField(DeckType, on_delete=models.deletion.CASCADE)


