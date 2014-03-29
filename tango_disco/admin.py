from django.contrib import admin
from tango_disco.models import *

admin.site.register(Song)
admin.site.register(Genre)
admin.site.register(Musician)
admin.site.register(Orchestra)
admin.site.register(Recording)
admin.site.register(PlayedOn)
admin.site.register(MusicianRole)
