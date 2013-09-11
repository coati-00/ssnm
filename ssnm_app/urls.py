from django.conf.urls import patterns, url

from ssnm_app import views

urlpatterns = patterns(
    '',
    url(r'^ssnmapp/$', views.index, name='index'),
    url(r'^help/$', views.help, name='help'),
    url(r'^about/$', views.about, name='about'),
    #url(r'^guest_login/$', views.guest_login, name='guest_login'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^add_course/$', views.add_course, name='add_course'),
    #url(r'^course_created/$', views.course_created, name='course_created'),
    url(r'^home_page/$', views.home_page, name='home_page'),
    url(r'^show_students', views.show_students, name='show_students'),
    url(r'^(?P<user_uni>\d+)/user_courses/$', views.user_courses, name='user_courses'),
    url(r'^(?P<course>\d+)/course_students/$', views.show_course_students, name='show_course_students'),


)

