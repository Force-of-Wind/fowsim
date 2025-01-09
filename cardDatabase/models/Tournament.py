from django.db import models
from fowsim import constants as CONS

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
    #Format after PR is in

    def __str__(self):
        return self.title
    
class TournamentPlayer(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    registration_status = models.TextField(max_length=32, blank=True, null=True, default=None,
                                 choices=CONS.TOURNAMENT_PLAYER_REGISTRATION_STATES)
    user_data = models.JSONField(blank=False, null=False)
    notes = models.CharField(max_length=500, null=False, blank=False)
    deck = models.ForeignKey('DeckList', on_delete=models.CASCADE)
    standing = models.IntegerField(blank=False, null=False)
    dropped_out = models.JSONField(blank=False, null=False, default=False)


class TournamentStaff(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    # permissions = models.TextField(max_length=32, blank=True, null=True, default=None,
    #                              choices=CONS.DECK_LIST_LOCK_MODE_CHOICES)

