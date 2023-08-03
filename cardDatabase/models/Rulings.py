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

class Restriction(models.Model):
    tag = models.ForeignKey('Tag', related_name='restriction_tag', on_delete=models.CASCADE)
    restrictioned_tag = models.ForeignKey('Tag', null=True, on_delete=models.CASCADE)
    action = models.ForeignKey('RestrictionAction', null=True, on_delete=models.CASCADE)
    text = models.TextField(null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, blank=True)
    added_by = models.ForeignKey('Profile', null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        self.last_modified = datetime.datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.restrictioned_tag is not None:
            return f'{self.tag.name} restricts {self.restrictioned_tag.name} - {self.text[:40]}'
        return f'{self.tag.name} - {self.text[:40]}'
    
class RestrictionAction(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    technical_name = models.CharField(max_length=50, null=False, blank=False)
    def __str__(self):
        return f'{self.name[:40]} - {self.technical_name}'