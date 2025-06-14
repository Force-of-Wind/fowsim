from django.db import models
from fowsim import constants as CONS

class Tournament(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    meta_data = models.JSONField(null=False)
    is_online = models.BooleanField(null=False, blank=False, default=False)
    registration_deadline = models.DateTimeField(blank=False, null=False)
    registration_locked = models.BooleanField(null=False, blank=False, default=False)
    deck_edit_deadline = models.DateTimeField(blank=False, null=False)
    deck_edit_locked = models.BooleanField(null=False, blank=False, default=False)
    start_datetime = models.DateTimeField(blank=False, null=False)
    phase = models.TextField(max_length=32, blank=True, null=True, default=CONS.TOURNAMENT_PHASE_CREATED,
                                 choices=CONS.TOURNAMENT_PHASES)
    reveal_decklists = models.BooleanField(null=False, blank=False, default=False)
    format = models.ForeignKey('Format', on_delete=models.SET_NULL, null=True, blank=True)
    level = models.ForeignKey('TournamentLevel', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class TournamentPlayer(models.Model):
    profile = models.ForeignKey('Profile', related_name='tournament_player' , on_delete=models.CASCADE)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE, related_name='players')
    registration_status = models.TextField(max_length=32, blank=True, null=True, default=None,
                                 choices=CONS.TOURNAMENT_PLAYER_REGISTRATION_STATES)
    last_registration_updated_by = models.ForeignKey('Profile', on_delete=models.SET_NULL, blank=True, null=True, default=None)
    user_data = models.JSONField(null=False)
    notes = models.CharField(max_length=500, null=False, blank=True)
    deck = models.ForeignKey('DeckList', on_delete=models.CASCADE)
    standing = models.IntegerField(blank=False, null=False)
    dropped_out = models.BooleanField(blank=False, null=False, default=False)

    def __str__(self):
        return self.profile.user.username


class TournamentStaff(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    role = models.ForeignKey('StaffRole', on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.user.username


class TournamentLevel(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False)
    code = models.CharField(max_length=2, null=False, blank=False)
    hint = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.title
    

class StaffRole(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    can_read = models.BooleanField(null=False, blank=False, default=True)
    can_write = models.BooleanField(null=False, blank=False, default=False)
    can_delete = models.BooleanField(null=False, blank=False, default=False)
    default = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return self.title