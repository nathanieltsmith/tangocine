from django.db import models
from tango_disco.models import Recording

# Create your models here.
class Performer(models.Model):
	firstName = models.CharField(max_length=30)
	lastName = models.CharField(max_length=30)
	code = models.CharField(max_length=10, null=True, blank=True)

	def __unicode__(self):              # __unicode__ on Python 2
		return self.firstName +' '+ self.lastName

class Couple(models.Model):
	performers = models.ManyToManyField(Performer)
	def __unicode__(self):              # __unicode__ on Python 2
		try: 
			return self.performers.first().__unicode__() + ' and ' + self.performers.last().__unicode__();
		except:
			return 'blah'

class EventSeries(models.Model):
	name = models.CharField(max_length=300)

	def __unicode__(self):              # __unicode__ on Python 2
		return self.name

class DanceEvent(models.Model):
	name = models.CharField(max_length=300)
	date = models.DateField()
	eventSeries = models.ForeignKey(EventSeries)

	def __unicode__(self):              # __unicode__ on Python 2
		return self.name

class Performance(models.Model):
	PERFORMANCE_TYPES = (
        ('P', 'Performance'),
        ('D', 'Class Demo'),
        ('I', 'Standalone Instructional Video'),
        ('S', 'Social Dancing')
    )
	couples = models.ManyToManyField(Couple)
	recordings = models.ManyToManyField(Recording, null=True, blank=True)
	youtubeId = models.CharField(max_length=30)
	event = models.ForeignKey(DanceEvent, null=True, blank=True)
	performance_type = models.CharField(max_length=1, choices=PERFORMANCE_TYPES)
	performance_date = models.DateField(null=True, blank=True)
	created_date = models.DateTimeField(auto_now_add=True, editable=False)
	def __unicode__(self):
		return self.couples.first().__unicode__() + ': ' + self.recordings.first().__unicode__()  



