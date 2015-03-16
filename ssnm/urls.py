import os.path

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from registration.backends.default.views import RegistrationView

from ssnm.main.models import CreateAccountForm


admin.autodiscover()

# site_media_root = os.path.join(os.path.dirname(__file__), "../media")

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
logout_page = (r'^logout/$',
               'django.contrib.auth.views.logout',
               {'next_page': redirect_after_logout})
admin_logout_page = (r'^accounts/logout/$',
                     'django.contrib.auth.views.logout',
                     {'next_page': '/admin/'})

if hasattr(settings, 'CAS_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (r'^logout/$',
                   'djangowind.views.logout',
                   {'next_page': redirect_after_logout})
    admin_logout_page = (r'^admin/logout/$',
                         'djangowind.views.logout',
                         {'next_page': redirect_after_logout})

urlpatterns = patterns(
    '',
    logout_page,
    admin_logout_page,
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
    #(r'^help/$', 'ssnm.main.views.help_page'),
    (r'^help/$', TemplateView.as_view(template_name="help.html"), {},
     "help-page"),
    (r'^about/$', TemplateView.as_view(template_name="about.html"), {},
     "about-page"),
    #(r'^about/$', 'ssnm.main.views.about'),
    (r'^contact/$', 'ssnm.main.views.contact'),
    (r'^logout/$',
     'django.contrib.auth.views.logout',
     {'next_page': '/'}),
    #(r'^thanks/$', 'ssnm.main.views.thanks'),
    (r'^thanks/$', TemplateView.as_view(template_name="thanks.html"), {},
     "thanks-page"),
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

)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

