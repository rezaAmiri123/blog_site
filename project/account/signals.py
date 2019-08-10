from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile, User


@receiver(post_save, sender=User)
def build_profile_on_user_creation(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
