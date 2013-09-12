from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.conf.urls import patterns, url
import staticmedia
import os.path
from ecomap import views
site_media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    '',
    url(r'^help/$', views.help, name='help'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^guest_login/$', views.guest_login, name='guest_login'),
    url(r'^ecomap/(?P<map_id>\d+)/$', views.get_map, name='get_map'),
    url(r'^ecomap/(?P<map_id>\d+)/display/flashConduit$', views.display, name='display'),
    url(r'^ecomap/$', views.ecomap, name='game'),
    url(r'^ecomap/display/flashConduit$', views.display, name='display'),
    url(r'^show_maps/$', views.show_maps, name='show_maps'),
    #url(r'^home/$', views.home, name='home'),
    #url(r'^show_all_students', views.show_all_students, name='show_all_students'),
    #url(r'^show_all_maps', views.show_all_students, name='show_all_students'),

    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/ecomap/media'}),

) + staticmedia.serve()
