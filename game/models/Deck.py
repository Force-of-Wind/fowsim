from django.db import models


class DeckType(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)


class Deck(models.Model):
    type = models.OneToOneField(DeckType, on_delete=models.deletion.CASCADE)


