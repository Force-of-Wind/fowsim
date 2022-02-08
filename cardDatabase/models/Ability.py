from django.db import models

from fowsim.utils import AbstractModel


class Ability(AbstractModel):
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.text

    @classmethod
    def get_type_choices(cls):
        return super().get_type_choices_from_cls(cls)

    @classmethod
    def get_cls(cls):
        return cls


class AutomaticAbilityTrigger(Ability):
    class Meta:
        abstract = False
        app_label = 'cardDatabase'
    # event = ForeignKey(Event.GameEvent)


class AutomaticAbility(Ability):
    class Meta:
        abstract = False
        app_label = 'cardDatabase'

    trigger = models.ManyToManyField(AutomaticAbilityTrigger)
    triggered_count = models.IntegerField(default=0, null=False, blank=False)


class ContinuousAbility(Ability):
    class Meta:
        abstract = False
        app_label = 'cardDatabase'

    #effect = models.ForeignKey(Effect, on_delete=models.CASCADE)


class ActivateAbility(Ability):
    class Meta:
        abstract = False
        app_label = 'cardDatabase'


class Keyword(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=200, blank=False, null=False)
    search_string = models.CharField(max_length=200, blank=False, null=False)