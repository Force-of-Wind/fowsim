import os
import re

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles import finders

from cardDatabase.models.Effects import Effect
from fowsim.utils import listToChoices, AbstractModel
from fowsim import constants as CONS


class Cluster(models.Model):
    class Meta:
        app_label = 'cardDatabase'

    name = models.CharField(max_length=200, null=False, blank=False)


class Set(models.Model):
    class Meta:
        app_label = 'cardDatabase'

    name = models.CharField(max_length=200, null=False, blank=False)
    code = models.CharField(max_length=200, null=False, blank=False)
    cluster = models.ForeignKey('Cluster', on_delete=models.CASCADE)


class Race(models.Model):
    class Meta:
        app_label = 'cardDatabase'

    name = models.CharField(max_length=200, null=False, blank=False)


class AbilityText(models.Model):
    text = models.TextField(null=False, blank=False)


class Type(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False, choices=listToChoices(CONS.CARD_TYPE_VALUES))


class Card(AbstractModel):
    class Meta:
        abstract = False
        app_label = 'cardDatabase'
    name = models.CharField(max_length=200, null=False, blank=False)
    name_without_punctuation = models.CharField(max_length=200, null=False, blank=False)
    card_id = models.CharField(max_length=200, null=False, blank=False)
    cost = models.CharField(max_length=200, null=False, blank=False)
    divinity = models.CharField(max_length=200, null=False, blank=False)
    flavour = models.TextField(null=False, blank=False)
    races = models.ManyToManyField('Race', related_name='races')
    rarity = models.CharField(max_length=200, null=False, blank=False, choices=CONS.RARITY_CHOICE_VALUES)
    ATK = models.CharField(max_length=200, null=False, blank=False)
    DEF = models.CharField(max_length=200, null=False, blank=False)
    types = models.ManyToManyField('Type', related_name='types')
    ability_texts = models.ManyToManyField('AbilityText', related_name='ability_texts')

    def __str__(self):
        return self.name

    @classmethod
    def get_cls(cls):
        return cls

    @classmethod
    def get_type_choices(cls):
        super().get_type_choices_from_cls(cls)

    @property
    def card_image_filename(self):
        if finders.find(f'cards/{self.card_id}.jpg'):
            return self.card_id + '.jpg'
        else:  # Try use the "front" side of a card, might be an alternative card
            return self.card_id.replace(CONS.DOUBLE_SIDED_CARD_CHARACTER, '') + '.jpg'

    @property
    def set_code(self):
        return self.card_id.split('-')[0]

    @property
    def total_cost(self):
        total = 0
        matches = re.findall('{[a-zA-Z0-9]*}', self.cost)
        for match in matches:  # "{W}" or "{R}" or "{3}" etc.
            cost_value = match[1]
            if cost_value.isnumeric():
                total += int(cost_value)
            elif cost_value == 'X':
                pass
            else:
                total += 1

        return total



class Chant(models.Model):
    class Meta:
        app_label = 'cardDatabase'
    card = models.ForeignKey('Card', on_delete=models.CASCADE)
    #abilities = models.ManyToManyField('Ability')
    effect_type_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=Effect.get_type_choices)
    effect_type_id = models.PositiveIntegerField()
    effect_type = GenericForeignKey('effect_type_type', 'effect_type_id')
