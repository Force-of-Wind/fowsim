import datetime

from django.db import models


class Ruling(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE)
    text = models.TextField(null=False, blank=False)
    company_confirmed = models.BooleanField(null=False, blank=False, default=False)
    last_modified = models.DateTimeField(auto_now_add=True, blank=True)
    added_by = models.ForeignKey('Profile', null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        self.last_modified = datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.card.name} - {self.text[:40]}'
