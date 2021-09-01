from django.db import models

from . import Area
from fowsim.utils import AbstractModel


class GameEvent(AbstractModel):
    description = models.TextField(blank=False, null=False)

    @classmethod
    def get_type_choices(cls):
        return super().get_type_choices_from_cls(cls)

    def __str__(self):
        return self.description

    @classmethod
    def get_cls(cls):
        return cls


class MoveCard(GameEvent):
    from_area = models.ManyToManyField(Area, related_name="from_area")
    to_area = models.ManyToManyField(Area, related_name="to_area")

    def __str__(self):
        return 'Moves card from %s to %s' % (self.from_area.name, self.to_area.name)

    @classmethod
    def get_concrete_cls(cls):
        return cls