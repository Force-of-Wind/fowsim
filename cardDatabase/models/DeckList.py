from django.utils import timezone

from django.db import models

from .User import Profile
from fowsim import constants as CONS


class DeckList(models.Model):
    def __str__(self):
        return f'{self.name} ({self.profile.user.email})'

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=100000, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, blank=True)
    comments = models.TextField(max_length=10000, blank=True, null=True, default='')
    public = models.BooleanField(default=True, blank=False, null=False)
    shareCode = models.TextField(max_length=32, blank=True, null=True, default='')
    shareMode = models.TextField(max_length=32, blank=True, null=True, default='',
                                 choices=CONS.DECK_LIST_SHARE_MODE_CHOICES)
    deck_type = models.CharField(max_length=32,choices=CONS.DECK_TYPE_CHOICES, blank=False, null=False, default=CONS.DECK_TYPE_WANDERER)

    def save(self, *args, **kwargs):
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)

    @property
    def get_colours(self):
        colours = self.cards.all().values_list('card__colours__db_representation', flat=True).distinct()
        colours = [x for x in colours if not x == CONS.ATTRIBUTE_VOID_CODE]
        if len(colours) == 0:
            colours = [CONS.ATTRIBUTE_VOID_CODE]
        return colours
    
    @property
    def get_front_card_of_deck(self):
        front_card = self.cards.order_by('position').first()
        return front_card


class DeckListCard(models.Model):
    def __str__(self):
        return f'{self.card.name} ({self.decklist.profile.user.email}: {self.decklist.name})'
    decklist = models.ForeignKey(DeckList, null=False, blank=False, related_name='cards', on_delete=models.CASCADE)
    card = models.ForeignKey('Card', null=False, blank=False, on_delete=models.CASCADE)
    position = models.IntegerField(blank=False, null=False)
    zone = models.ForeignKey('UserDeckListZone', blank=False, null=False, on_delete=models.CASCADE, related_name='cards')
    quantity = models.IntegerField(blank=False, null=False, default=1)


class DeckListZone(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=10000, blank=False, null=False)
    show_by_default = models.BooleanField(blank=False, null=False, default=False)
    position = models.IntegerField(blank=True, null=True)


class UserDeckListZone(models.Model):
    decklist = models.ForeignKey('DeckList', on_delete=models.CASCADE)
    position = models.IntegerField(blank=False, null=False)
    zone = models.ForeignKey('DeckListZone', on_delete=models.CASCADE)

    @property
    def card_count(self):
        return self.cards.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
