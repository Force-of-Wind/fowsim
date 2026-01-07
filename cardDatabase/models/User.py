from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    site_admin = models.BooleanField(null=False, blank=False, default=False)
    is_judge = models.BooleanField(null=False, blank=False, default=False)
    can_create_tournament = models.BooleanField(null=False, blank=False, default=True)
    see_debug_toolbar = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
