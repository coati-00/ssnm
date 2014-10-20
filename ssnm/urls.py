from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from ssnm.main.models import CreateAccountForm
from registration.backends.default.views import RegistrationView
import os.path
admin.autodiscover()


site_media_root = os.path.join(os.path.dirname(__file__), "../media")

auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'CAS_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))

urlpatterns = patterns(
    '',
    auth_urls,
    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm),
        name='registration_register'),
    url(r'^accounts/password_reset/$',
        'django.contrib.auth.views.password_reset',
        name='password_reset'),
    url(r'^accounts/password_reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^accounts/reset/done/$',
        'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),

    (r'^$', 'ssnm.main.views.show_maps'),
    (r'^help/$', 'ssnm.main.views.help_page'),
    (r'^about/$', 'ssnm.main.views.about'),
    (r'^contact/$', 'ssnm.main.views.contact'),
    (r'^logout/$',
     'django.contrib.auth.views.logout',
     {'next_page': '/'}),
    (r'^thanks/$', 'ssnm.main.views.thanks'),
    (r'^ecomap/$', 'ssnm.main.views.get_map'),
    (r'^ecomap/(?P<map_id>\d+)/$', 'ssnm.main.views.get_map'),
    (r'^ecomap/(?P<map_id>\d+)/display/flashConduit$',
     'ssnm.main.views.display'),
    (r'^details/(?P<map_id>\d+)/$', 'ssnm.main.views.get_map_details'),
    (r'^ecomap/(?P<map_id>\d+)/delete_map/$', 'ssnm.main.views.delete_map'),
    (r'^ecomap/(?P<map_id>\d+)/display/back_to_list_button_clicked$',
     'ssnm.main.views.go_home'),
    (r'^details/$', 'ssnm.main.views.get_map_details'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
