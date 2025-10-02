# ----------------------------------------------------------------------------------------------
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from app_devices.models import DeviceInfo
# ----------------------------------------------------------------------------------------------


# **********************************************************************************************
class Profile(models.Model):
    # ----------------------------------------------------------------------------------------------
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='user_avatar', blank=True, null=True, verbose_name='Avatar')
    birth_date = models.DateField(default=now, blank=True, null=True, verbose_name='Birth Date')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Contact Number')
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='Email')
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name='City')
    country = models.CharField(max_length=30, blank=True, null=True, verbose_name='Country')
    BLOOD_GROUP = (
        ('na', 'NA'), ('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'), ('ab+', 'AB+'), ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP, blank=True, null=True, verbose_name='Blood Group')
    acc_status = models.BooleanField(default=False, verbose_name='Active Status')
    # ----------------------------------------------------------------------------------------------
    assigned_cameras = models.ManyToManyField(DeviceInfo, blank=True, related_name='Profile_assigned_cameras', verbose_name='Assigned Device')
    # ----------------------------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = '01. Profile'
        verbose_name_plural = '01. Profiles'

    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    def __str__(self):

        return f"{self.user.username}, " \
               f"{self.birth_date}, " \
               f"{self.phone_number}, " \
               f"{self.email}, " \
               f"{self.city}, "\
               f"{self.country}, " \
               f"{self.blood_group}, " \
               f"{self.acc_status}, " \
               f"{self.assigned_cameras}"
    # ----------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
# ----------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
# ----------------------------------------------------------------------------------------------
# **********************************************************************************************
