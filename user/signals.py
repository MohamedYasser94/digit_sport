from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.db.models.signals import post_save
from django.dispatch import receiver


from user.models import UserProfile, UserGeoInfo

User = get_user_model()
UserModel = get_user_model()
user_logged_in = Signal()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, note='signals')
        UserGeoInfo.objects.create(user=instance)



# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.user.save()

