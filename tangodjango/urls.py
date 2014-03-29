from django.conf.urls import patterns, include, url

from django.contrib import admin
import autocomplete_light
# import every app/autocomplete_light_registry.py
autocomplete_light.autodiscover()
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^grappelli/', include('grappelli.urls')), 
	url(r'^admin/', include(admin.site.urls)),
    url(r'^u/', include('tango_perfs.urls')),
    url(r'^', include('tango_perfs.urls')),
    url(r'^foundation', include('foundation.urls')),
    
)