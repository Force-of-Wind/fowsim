import abc

from django.db import models

from . import Area
from fowsim.utils import AbstractModel, listToChoices
from fowsim import constants as CONS


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

    def can_do_action(self, data):
        """
        :return: Boolean whether the action is able to be done (not replacement effects)
        """
        return True

    def apply_replacement_effects(self, data):
        """
        :return: Boolean if replacement effect was applied
        """
        return False

    @abc.abstractmethod
    def do_action(self, data):
        """
        Action is able to be done, replacement effects have been applied to the necessary data/fields. Do the action
        :return:
        """

    def apply_action(self, data):
        if self.can_do_action(data):
            self.apply_replacement_effects(data)
            self.do_action(data)
        else:
            raise Exception("Action %s could not be done") % (str(self))


# Turn the values into tuples
MOVE_CARD_POSITION_CHOICES = listToChoices(CONS.MOVE_CARD_POSITION_CHOICES_VALUES)
EFFECT_AREA_CONTROLLER_CHOICES = listToChoices(CONS.EFFECT_AREA_CHOICES_VALUES)


class MoveCardFromPosition(GameEvent):
    from_area = models.ManyToManyField(Area, related_name="from_area")
    from_position = models.TextField(choices=MOVE_CARD_POSITION_CHOICES)
    from_controller = models.TextField(choices=EFFECT_AREA_CONTROLLER_CHOICES)
    to_area = models.ManyToManyField(Area, related_name="to_area")
    to_position = models.TextField(choices=MOVE_CARD_POSITION_CHOICES)
    to_controller = models.TextField(choices=EFFECT_AREA_CONTROLLER_CHOICES)

    def __str__(self):
        return 'Moves card from %s in position %s to %s in position %s' % (
            self.from_area.name, self.from_position, self.to_area.name, self.to_position)

    def do_action(self, data):
        cards_to_move = data['cards_to_move']
        for card in cards_to_move:


    @classmethod
    def get_concrete_cls(cls):
        return cls
