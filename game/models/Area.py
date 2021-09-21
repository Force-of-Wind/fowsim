from django.db import models


class Area(models.Model):
    class Meta:
        app_label = 'game'

    name = models.CharField(max_length=200, null=False, blank=False)
    is_zone = models.BooleanField(default=True, blank=False, null=False)

    def __str__(self):
        return self.name
