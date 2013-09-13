'''Administer Ecouser and Ecomap from the
adming interface.'''
from ecomap.models import Ecouser, Ecomap
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class EcouserInline(admin.StackedInline):
    '''Associating Ecouser with User object.'''
    model = Ecouser
UserAdmin.inlines = [EcouserInline, ]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Ecomap)
