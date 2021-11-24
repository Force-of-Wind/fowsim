from django.db import models

from .User import Profile


class DeckList(models.Model):
    def __str__(self):
        return f'{self.name} ({self.profile.user.email})'

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=False, blank=False)


class DeckListCard(models.Model):
    def __str__(self):
        return f'{self.card.name} ({self.decklist.profile.user.email}: {self.decklist.name})'
    decklist = models.ForeignKey(DeckList, null=False, blank=False, related_name='cards', on_delete=models.CASCADE)
    card = models.ForeignKey('Card', null=False, blank=False, on_delete=models.CASCADE)
    position = models.IntegerField(blank=False, null=False)
    zone = models.ForeignKey('DeckListZone', blank=False, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, null=False, default=1)


class DeckListZone(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=200, blank=False, null=False)
    show_by_default = models.BooleanField(blank=False, null=False, default=False)