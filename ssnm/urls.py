from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template
from ecomap.models import CreateAccountForm
from registration.backends.default.views import RegistrationView
import os.path
admin.autodiscover()
import staticmedia

site_media_root = os.path.join(os.path.dirname(__file__), "../media")

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
logout_page = (
    r'^accounts/logout/$',
    'django.contrib.auth.views.logout',
    {'next_page': redirect_after_logout})
if hasattr(settings, 'WIND_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (
        r'^accounts/logout/$',
        'djangowind.views.logout',
        {'next_page': redirect_after_logout})

urlpatterns = patterns(
    '',
    auth_urls,
    logout_page,
    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm),
        name='registration_register'),

    (r'^$', 'ecomap.views.login'),
    (r'^help/$', 'ecomap.views.help_page'),
    (r'^about/$', 'ecomap.views.about'),
    (r'^contact/$', 'ecomap.views.contact'),
    (r'^thanks/$', 'ecomap.views.thanks'),

    (r'^ecomap/$', 'ecomap.views.ecomap'),
    (r'^ecomap/display/flashConduit$', 'ecomap.views.display'),

    #(r'^ecomap/(?P<map_id>\d+)/$', 'ecomap.views.get_map'),
    #(r'^ecomap/(?P<map_id>\d+)/display/flashConduit$', 'ecomap.views.display'),

    (r'^show_maps/$', 'ecomap.views.show_maps'),
    (r'^create_account/$', 'ecomap.views.create_account'),
    (r'^register/$', 'ecomap.views.create_account'),
    (r'^ecomap/(?P<map_id>\d+)/delete_map/$', 'ecomap.views.delete_map'),
# taken from nynjaetc
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^munin/', include('munin.urls')),
    (r'^stats/', direct_to_template, {'template': 'stats.html'}),
    (r'smoketest/', include('smoketest.urls')),
    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
) + staticmedia.serve()





'''
#from django.conf.urls.defaults import *
#from django.contrib import admin
#from django.conf import settings
from django.conf.urls import patterns, url
import staticmedia
import os.path
from ecomap import views
site_media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    '',
    url(r'^help/$', views.help_page, name='help'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^ecomap/(?P<map_id>\d+)/$', views.get_map, name='get_map'),
    url(r'^ecomap/(?P<map_id>\d+)/display/flashConduit$', views.display, name='display'),
    url(r'^ecomap/$', views.ecomap, name='game'),
    url(r'^ecomap/display/flashConduit$', views.display, name='display'),
    url(r'^show_maps/$', views.show_maps, name='show_maps'),
    url(r'^$', views.home, name='ecomap'),
    url(r'^create_account/$', views.create_account, name='create_account'),
    #url(r'^show_all_students', views.show_all_students, name='show_all_students'),
    #url(r'^show_all_maps', views.show_all_students, name='show_all_students'),

    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/ecomap/media'}),

) + staticmedia.serve()
'''