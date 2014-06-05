from django.db import models
from unidecode import unidecode

class Musician(models.Model):
	firstName = models.CharField(max_length=200)
	lastName = models.CharField(max_length=200)
	simplifiedName = models.CharField(max_length=400, null=True, blank=True)

	def __unicode__(self):
		return self.lastName + ', ' + self.firstName

class MusicianRole(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __unicode__(self):
		return self.name


class RecordLabel(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self):              # __unicode__ on Python 2
		return self.name

class Genre(models.Model):
	name = models.CharField(max_length=40, unique=True)
	def __unicode__(self):              # __unicode__ on Python 2
		return self.name

# Create your models here.
class Song(models.Model):
	title = models.CharField(max_length=300, unique=True)
	simplifiedTitle = models.CharField(max_length=300, unique=True, null=True, blank=True)
	composer = models.ManyToManyField(Musician, null=True, blank=True)
	lyricist = models.ManyToManyField(Musician,related_name='composer', null=True, blank=True)

	def __unicode__(self):              # __unicode__ on Python 2
		return self.title

	def merge(self, song):
		for recording in Recording.objects.filter(song=song):
			recording.song_id = self.pk
			recording.save()
			#song.delete()
	def save(self, *args, **kwargs):
		self.simplifiedTitle = unidecode(self.title).lower()
		super(Song, self).save(*args, **kwargs) # Call the "real" save() method.
		


class Orchestra(models.Model):
	leader = models.ForeignKey(Musician)
	name = models.CharField(max_length=200)
	ocode = models.CharField(max_length=30, unique=True)
	def __unicode__(self):              # __unicode__ on Python 2
		return self.name

	def performanceCount(self):
		from tango_perfs.models import Performance
		return len(Performance.objects.filter(recordings__orchestra=self))

	performanceCount.number = True
	performanceCount.short_description = 'Total Performances'


class Recording(models.Model):
	song = models.ForeignKey(Song)
	orchestra = models.ForeignKey(Orchestra)
	label = models.ForeignKey(RecordLabel, null=True, blank=True)
	genre = models.ForeignKey(Genre)
	recorded = models.DateField(null=True, blank = True)
	discNo = models.CharField(max_length=20, null=True, blank=True)
	matrixNo = models.CharField(max_length=20, null=True, blank=True)
	itunesId = models.CharField(max_length=100, null=True, blank=True)
	youtubeId = models.CharField(max_length=20, null=True, blank=True)

	def __unicode__(self):              # __unicode__ on Python 2
		try:
			return self.song.title + ' (' + self.orchestra.name + ', ' + self.recorded.strftime('%Y') + ')'
		except Exception, e:
			return self.song.title + ' (' + self.orchestra.name + ')'
		

class PlayedOn(models.Model):
	musician = models.ForeignKey(Musician)
	recording = models.ForeignKey(Recording)
	role = models.ForeignKey(MusicianRole)