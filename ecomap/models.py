'''Models for Ecouser and Ecomap. Ecouser is an extension of the User Profile'''
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Ecouser(models.Model):
    '''Stores Ecouser profile with User profile if User uses Ecomaps'''

    class Meta:
        verbose_name_plural = "users"

    user = models.OneToOneField(User, unique=True)

    USER_STATUS_CHOICES = (
        ('IN', 'Instructor'),
        ('ST', 'Student'),
        ('AD', 'Administrator'),
    )
    status = models.CharField(max_length=2, choices=USER_STATUS_CHOICES, default='ST')
    uni = models.CharField(max_length=50)

    def __unicode__(self):
        return self.user.first_name + " " + self.user.last_name


def create_user_profile(sender, instance, created, **kwargs):
    '''method that associates Ecouser with User object'''
    if created:
        profile, created = Ecouser.objects.get_or_create(user=instance)
    post_save.connect(create_user_profile, sender=User)



class Ecomap(models.Model):
    '''Store Ecomap and associated information'''
    name = models.CharField(max_length=50)
    ecomap_xml = models.TextField()
    owner = models.ForeignKey('Ecouser') # an ecomap must have an owner or creator
