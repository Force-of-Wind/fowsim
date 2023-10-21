import os
import re
import sys

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.dispatch import receiver
from django.db.models.signals import pre_save

from cardDatabase.models.Effects import Effect
from cardDatabase.models.Rulings import Ruling
from cardDatabase.models.Banlist import BannedCard, CombinationBannedCards
from fowsim.utils import listToChoices, AbstractModel
from fowsim import constants as CONS

from io import BytesIO
from PIL import Image

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

    def __str__(self):
        return self.name

    name = models.CharField(max_length=200, null=False, blank=False)


class AbilityText(models.Model):
    def __str__(self):
        return self.text
    text = models.TextField(null=False, blank=False)


class Type(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=200, null=False, blank=False, choices=listToChoices(CONS.CARD_TYPE_VALUES))


class CardAbility(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='abilities')
    ability_text = models.ForeignKey('AbilityText', on_delete=models.CASCADE, related_name='card')
    position = models.IntegerField(blank=False, null=False, default=1)

class Tag(models.Model):
    def __str__(self):
        return self.name    
    name = models.CharField(max_length=200, null=False, blank=False)

class Card(AbstractModel):
    class Meta:
        abstract = False
        app_label = 'cardDatabase'
    name = models.CharField(max_length=200, null=False, blank=False)
    name_without_punctuation = models.CharField(max_length=200, null=False, blank=False)
    card_id = models.CharField(max_length=200, null=False, blank=False)
    card_image = models.ImageField(default=None, blank=True, null=True, upload_to='cards')
    cost = models.CharField(max_length=200, null=True, blank=True)
    divinity = models.CharField(max_length=200, null=True, blank=True)
    flavour = models.TextField(null=True, blank=True)
    races = models.ManyToManyField('Race', related_name='races', blank=True)
    rarity = models.CharField(max_length=200, null=False, blank=True, choices=CONS.RARITY_CHOICE_VALUES)
    ATK = models.IntegerField(null=True, blank=True)
    DEF = models.IntegerField(null=True, blank=True)
    types = models.ManyToManyField('Type', related_name='types')
    ability_texts = models.ManyToManyField('AbilityText', related_name='cards', blank=True, through=CardAbility)
    colours = models.ManyToManyField('CardColour', related_name='cards', blank=False)
    tag = models.ManyToManyField('Tag', related_name='cards', blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_cls(cls):
        return cls

    @classmethod
    def get_type_choices(cls):
        super().get_type_choices_from_cls(cls)

    @property
    def set_code(self):
        return self.card_id.split('-')[0]

    @property
    def set_number(self):
        splits = self.card_id.split('-')
        if len(splits) > 1:
            return splits[1]
        return None

    @property
    def total_cost(self):
        total = 0
        if self.cost:
            matches = re.findall('{[a-zA-Z0-9]*}', self.cost)
            for match in matches:  # "{W}" or "{R}" or "{3}" or "{10}" etc.
                cost_value = match[1:-1]
                if cost_value.isnumeric():
                    total += int(cost_value)
                elif cost_value == 'X':
                    pass
                else:
                    total += 1

        return total

    @property
    def bans(self):
        return BannedCard.objects.filter(card__name=self.name)

    @property
    def combination_bans(self):
        return CombinationBannedCards.objects.filter(cards__name=self.name)

    @property
    def other_sides(self):
        shared_id = self.card_id
        self_other_side_char = ''
        for to_remove in CONS.OTHER_SIDE_CHARACTERS:
            if to_remove in shared_id:
                shared_id = shared_id.replace(to_remove, '')
                self_other_side_char = to_remove

        other_side_query = Q()

        if self_other_side_char:
            # This isn't the front side so check with no extra chars
            other_side_query |= Q(card_id=shared_id)

        # Also check all the other combinations of characters that aren't itself
        for to_query in CONS.OTHER_SIDE_CHARACTERS:
            if not self_other_side_char == to_query: # Don't look for self
                other_side_query |= Q(card_id=shared_id + to_query)

        return Card.objects.filter(other_side_query)

    @property
    def rulings(self):
        return Ruling.objects.filter(card__name=self.name)

    @property
    def reprints(self):
        return Card.objects.filter(name=self.name).filter(~Q(id=self.id))


class Chant(models.Model):
    class Meta:
        app_label = 'cardDatabase'
    card = models.ForeignKey('Card', on_delete=models.CASCADE)
    #abilities = models.ManyToManyField('Ability')
    effect_type_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=Effect.get_type_choices)
    effect_type_id = models.PositiveIntegerField()
    effect_type = GenericForeignKey('effect_type_type', 'effect_type_id')


class CardColour(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=200, blank=False, null=False)
    db_representation = models.CharField(max_length=200, blank=False, null=False)


@receiver(pre_save, sender=Card)
def resize_image_if_new(sender, instance, **kwargs):
    obj = None
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        obj = None
        pass
    finally:
        if (not obj and instance.card_image) or (obj and obj.card_image != instance.card_image and instance.card_image):
            size = 480, 670
            im = Image.open(instance.card_image)
            if im.mode == 'P':
                im = im.convert('RGBA')

            if im.mode == "RGBA":
                new_image = Image.new("RGBA", im.size, "WHITE")
                new_image.paste(im, (0, 0), im)
                im = new_image
                im = im.convert("RGB")
            im = im.resize(size, Image.ANTIALIAS)
            im_io = BytesIO()
            im.save(im_io, 'JPEG', quality=70)
            instance.card_image = InMemoryUploadedFile(im_io, 'ImageField', f"{instance.card_id}.jpg", 'image/jpeg', sys.getsizeof(im_io), None)
