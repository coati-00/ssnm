'''Models for Ecouser and Ecomap. Ecouser is an extension of the User Profile'''
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from registration.forms import RegistrationForm


class CreateAccountForm(RegistrationForm):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''
    first_name = forms.CharField(max_length=25, required=True, label="First Name")
    last_name = forms.CharField(max_length=25, required=True, label="Last Name")
    username = forms.CharField(max_length=25, required=True, label="Username")
    password1 = forms.CharField(max_length=25, widget=forms.PasswordInput, required=True, label="Password")
    password2 = forms.CharField(max_length=25, widget=forms.PasswordInput, required=True, label="Confirm Password")
    email = forms.EmailField()

    def clean(self):
        return super(RegistrationForm, self).clean()

    def clean_choice(self, field_name):
        if self.cleaned_data[field_name] == u"-----":
            msg = u"This field is required."
            self._errors[field_name] = self.error_class([msg])
            del self.cleaned_data[field_name]
            return None
        else:
            return self.cleaned_data[field_name]


class EcomapManager(models.Manager):
    def create_ecomap(self, owner):
        ecomap = self.create(owner=owner)

        return ecomap


class Ecomap(models.Model):
    '''Store Ecomap and associated information'''
    name = models.CharField(max_length=50)
    ecomap_xml = models.TextField()
    owner = models.ForeignKey(User)
    descriptions = models.TextField()
    objects = EcomapManager()
