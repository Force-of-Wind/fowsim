import datetime

from django.db import models

from .User import Profile

class Collection(models.Model):
    def __str__(self):
        return f'{self.name} ({self.profile.user.email})'

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now_add=True, blank=True)

    def save(self, *args, **kwargs):
        self.last_modified = datetime.datetime.now()
        super().save(*args, **kwargs)

class CollectionCard(models.Model):
    def __str__(self):
        return f'{self.card.name}'
    collection = models.ForeignKey(Collection, null=False, blank=False, related_name='cards', on_delete=models.CASCADE)
    card = models.ForeignKey('Card', null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, null=False, default=1)
