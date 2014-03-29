from django.conf.urls import patterns, url

from tango_perfs import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^(?P<perf_id>\d+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
    
    url(r'^performer/(?P<performer_code>[a-zA-Z]+)/$', views.performer, name='performer'),
    # ex: /polls/5/vote/
    url(r'^(?P<couple_id>\d+)/couple/$', views.couple, name='couple'),
    url(r'^(?P<orc_id>\d+)/orchestra/$', views.orchestra, name='orchestra'),
    url(r'^addperf/$', views.addperf, name='addperf')
   # url(r'^', views.index, name='index')
)