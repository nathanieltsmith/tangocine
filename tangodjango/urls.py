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
    url(r'^avatar/', include('avatar.urls')),
    #url(r'^accounts/', include('authtools.urls')),
    url(r'^accounts/', include('allauth.urls')),
    #url(r'^avatar_crop/', include('avatar_crop.urls')),
   #url(r'^accounts/login/', 'django.contrib.auth.views.login', name='auth_login'),
    #url(r'^accounts/logout/', 'django.contrib.auth.views.logout', name='auth_logout'),
    #url(r'^av/$', 'django.views.generic.simple.redirect_to', {'url': '/avatar/change/'}),
)

from django.conf import settings

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('', (
        r'^site_media/media/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}
        ),
    ) 

