from django.db import models
from .User import Profile

class Tournament(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    meta_data = models.JSONField(blank=False, null=False)
    is_online = models.BooleanField(null=False, blank=False, default=False)
    deck_registration_deadline = models.DateTimeField(blank=False, null=False)
    deck_registration_locked = models.BooleanField(null=False, blank=False, default=False)
    deck_edit_deadline = models.DateTimeField(blank=False, null=False)
    deck_edit_locked = models.BooleanField(null=False, blank=False, default=False)
    tournament_finished = models.BooleanField(null=False, blank=False, default=False)
    reveal_decklists = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return self.user.username


