from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from game.models import Event
from fowsim.utils import AbstractModel


class Effect(AbstractModel):
    description = models.TextField(null=False, blank=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.description

    @classmethod
    def get_type_choices(cls):
        return super().get_type_choices_from_cls(cls)


class OneTimeEffect(Effect):
    class Meta:
        abstract = False

    event_type_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=Event.GameEvent.get_type_choices)
    event_type_id = models.PositiveIntegerField()
    event_type = GenericForeignKey('event_type_type', 'event_type_id')
