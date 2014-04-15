from django.conf.urls import patterns, url
from django.conf import settings

from tango_perfs import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^p/(?P<id>.+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
    
    url(r'^performer/(?P<performer_code>[a-zA-Z]+)/$', views.performer, name='performer'),
    url(r'^filter/(?P<performer1>[+|%|2|0|a-zA-Z]+)/(?P<performer2>[a-zA-Z]+)/(?P<orchestra>[a-zA-Z]+)/(?P<song>[+|%|2|0|a-zA-Z]+)/(?P<genre>[a-zA-Z]+)/(?P<sort_method>[\-|_|a-zA-Z]+)/', views.filter, name='filter'),
    #url(r'^(?P<couple_id>\d+)/couple/$', views.couple, name='couple'),
    url(r'^event/(?P<event_id>\d+)/$', views.event, name='event'),
   # url(r'^(?P<orc_id>\d+)/orchestra/$', views.orchestra, name='orchestra'),
    url(r'^addperf/$', views.addperf, name='addperf'),
    url(r'^addform/(?P<youtubeId>.+)/$$', views.addPerformance, name='addPerformance'),
    url(r'^prefilter/$', views.prefilter, name='prefilter'),
	url(r'^api/get_songs/', views.get_songs, name='get_songs'),
    url(r'^accounts/register/$', views.SignUpView.as_view(), name='signup'),
    url(r'^accounts/login/$', views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', views.LogOutView.as_view(), name='logout'),
   # url(r'^', views.index, name='index')
)

urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))