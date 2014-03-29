import autocomplete_light
from django.contrib import admin
from tango_perfs.models import *
# Register your models here.


admin.site.register(Performer)

admin.site.register(DanceEvent)
admin.site.register(EventSeries)

class CoupleAdmin(admin.ModelAdmin):
	# This will generate a ModelForm
	form = autocomplete_light.modelform_factory(Couple)
admin.site.register(Couple)
admin.site.register(Performance)