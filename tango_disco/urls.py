from django.conf.urls import patterns, url
from django.conf import settings

from tango_disco import views

urlpatterns = patterns('',
    url(r'^radio/$', views.radio, name='radio'),

   # url(r'^', views.index, name='index')
)
