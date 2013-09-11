from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^flash/$', 'flash.views.display'),
    url(r'^test_file/$','flash.views.test')
#    url(r'^test_file', redirect_to, {'url': settings.STATIC_URL + 'as3.swf'}),
    #url(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),
    #url(r'^polls/(?P<poll_id>\d+)/results/$', 'polls.views.results'),
    #url(r'^polls/(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
    #url(r'^admin/', include(admin.site.urls)),
)