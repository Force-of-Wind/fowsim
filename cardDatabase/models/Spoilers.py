from django.db import models


class SpoilerSeason(models.Model):
    def __str__(self):
        return f'{self.set_code} - {"Active" if self.is_active else "Inactive"}'

    set_code = models.CharField(max_length=200, blank=False, null=False)
    is_active = models.BooleanField(blank=False, null=False, default=True)
