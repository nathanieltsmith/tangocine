from django.conf.urls import patterns, url
from django.conf import settings

from tango_radio import views


urlpatterns = patterns('',
    url(r'^tanda/$', views.radio, name='tanda'),
    url(r'^addtanda/$', views.add_tanda, name='add_tanda'),
    url(r'^api/tanda/$', views.get_tanda, name='get_tanda')
    url(r'^recordings/$', views.radio_recordings, name='list_recordings')
   # url(r'^', views.index, name='index')
)


