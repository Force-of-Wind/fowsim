from django.db import models

from fowsim.utils import AbstractModel


class Ability(AbstractModel):
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.text

    @classmethod
    def get_type_choices(cls):
        return super().get_type_choices_from_cls(cls)


class AutomaticAbilityTrigger(Ability):
    class Meta:
        abstract = False
    # event = ForeignKey(Event.GameEvent)


class AutomaticAbility(Ability):
    class Meta:
        abstract = False

    trigger = models.ManyToManyField(AutomaticAbilityTrigger)
    triggered_count = models.IntegerField(default=0, null=False, blank=False)


class ContinuousAbility(Ability):
    class Meta:
        abstract = False

    #effect = models.ForeignKey(Effect, on_delete=models.CASCADE)

class ActivateAbility(Ability):
    class Meta:
        abstract = False
