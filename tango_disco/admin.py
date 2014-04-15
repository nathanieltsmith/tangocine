from django.contrib import admin
from tango_disco.models import *

class SongAdmin(admin.ModelAdmin):
    list_display = ['title']

class OrcAdmin(admin.ModelAdmin):
    list_display = ['name', 'performanceCount']

class RecordingAdmin(admin.ModelAdmin):
	list_display = ['song', 'orchestra', 'recorded']
	search_fields = ['song__title', 'orchestra__name']

admin.site.register(Song, SongAdmin)
admin.site.register(Genre)
admin.site.register(Musician)
admin.site.register(Orchestra, OrcAdmin)
admin.site.register(Recording, RecordingAdmin)
admin.site.register(PlayedOn)
admin.site.register(MusicianRole)
