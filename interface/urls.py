from django.conf.urls import patterns, url
from django.conf import settings
import os.path
import staticmedia
from interface import views

site_media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    '',
    url(r'^interface/$', views.interface, name='interface'),
    #url(r'^help/$', views.help, name='help'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/usr/local/share/sandboxes/cdunlop/ssnm/interface/templates/interface/media'}),
)
