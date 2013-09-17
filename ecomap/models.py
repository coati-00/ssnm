'''Models for Ecouser and Ecomap. Ecouser is an extension of the User Profile'''
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Ecouser(models.Model):
    '''Stores Ecouser profile with User profile if User uses Ecomaps'''

    class Meta:
        '''put users when multiple ecousers are involved'''
        verbose_name_plural = "users"

    user = models.OneToOneField(User, unique=True)
    uni = models.CharField(max_length=50)

def create_user_profile(sender, instance, created, **kwargs):
    '''method that associates Ecouser with User object'''
    if created:
        profile, created = Ecouser.objects.get_or_create(user=instance)
    post_save.connect(create_user_profile, sender=User)


class Ecomap(models.Model):
    '''Store Ecomap and associated information'''
    name = models.CharField(max_length=50)
    ecomap_xml = models.TextField()
    owner = models.ForeignKey('Ecouser')
