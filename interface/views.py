from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.template import Context, loader
from django import forms
from django.views.generic.edit import FormView
#from ecomap.models import Course, Ecouser, Ecomap
#from django.forms import ModelForm

def interface(request):
    return render_to_response('interface/interface.html')
