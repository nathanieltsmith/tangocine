from django.conf.urls import patterns, url
from django.conf import settings

from tango_disco import views

urlpatterns = patterns('',
    url(r'^radio/$', views.radio, name='radio'),
    url(r'^discography$', views.index, name='discography'),
    url(r'^api/get_recordings$', views.get_recordings, name='get_recordings'),
    url(r'^api/report_error$', views.report_error, name='report_error'),
    url(r'^/api/update_recording/(?P<field>.+)/$', views.update_recording, name='update_recording'),
   # url(r'^', views.index, name='index')
)
