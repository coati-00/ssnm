from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template
from ssnm.main.models import CreateAccountForm
from registration.backends.default.views import RegistrationView
import os.path
admin.autodiscover()
import staticmedia






#    (r'^accounts/', include('registration.backends.default.urls')),
#    (r'^logout/$',
#     'django.contrib.auth.views.logout',
#     {'next_page': '/'}),


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
        {'next_page': '/'})#redirect_after_logout})

urlpatterns = patterns(
    '',
    auth_urls,
    logout_page,
    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm),
        name='registration_register'),
    (r'^$', 'ssnm.main.views.show_maps'),
    (r'^help/$', 'ssnm.main.views.help_page'),
    (r'^about/$', 'ssnm.main.views.about'),
    (r'^contact/$', 'ssnm.main.views.contact'),
    (r'^thanks/$', 'ssnm.main.views.thanks'),
    (r'^ecomap/$', 'ssnm.main.views.get_map'),
    (r'^ecomap/(?P<map_id>\d+)/$', 'ssnm.main.views.get_map'),
    (r'^ecomap/(?P<map_id>\d+)/display/flashConduit$', 'ssnm.main.views.display'),
    (r'^details/(?P<map_id>\d+)/$', 'ssnm.main.views.get_map_details'),
    (r'^ecomap/(?P<map_id>\d+)/delete_map/$', 'ssnm.main.views.delete_map'),
    (r'^details/$', 'ssnm.main.views.get_map_details'),
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


