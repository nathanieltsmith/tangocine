import autocomplete_light
from django.contrib import admin
from tango_perfs.models import *
# Register your models here.

def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)
deactivate.short_description = "Deactivate this performance"

admin.site.register(Article, ArticleAdmin)

class PerformerAdmin(admin.ModelAdmin):
	list_display = ['firstName', 'lastName', 'numPerfs', 'listPartners']

class PerformanceAdmin(admin.ModelAdmin):
	search_fields = ['couples__performers__firstName', 'couples__performers__lastName']
	actions = [deactivate]
admin.site.register(Performer, PerformerAdmin)

admin.site.register(DanceEvent)
admin.site.register(EventSeries)

class CoupleAdmin(admin.ModelAdmin):
	# This will generate a ModelForm
	form = autocomplete_light.modelform_factory(Couple)
admin.site.register(Couple)
admin.site.register(Performance, PerformanceAdmin)