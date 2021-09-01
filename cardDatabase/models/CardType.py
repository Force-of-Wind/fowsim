from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from . import Ability
from . import Effects

from fowsim.utils import AbstractModel


class Card(AbstractModel):
    name = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return '%s: %s' % (str(self.pk), self.name)

    @classmethod
    def get_type_choices(cls):
        super().get_type_choices_from_clas(cls)


class Chant(Card):
    class Meta:
        abstract = False
    abilities = models.ManyToManyField(Ability.Ability)
    effect_type_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                         limit_choices_to=Effects.Effect.get_type_choices)
    effect_type_id = models.PositiveIntegerField()
    effect_type = GenericForeignKey('effect_type_type', 'effect_type_id')