from django.db import models

class Musician(models.Model):
	firstName = models.CharField(max_length=200)
	lastName = models.CharField(max_length=200)

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
	composer = models.ManyToManyField(Musician, null=True, blank=True)
	lyricist = models.ManyToManyField(Musician,related_name='composer', null=True, blank=True)

	def __unicode__(self):              # __unicode__ on Python 2
		return self.title

class Orchestra(models.Model):
	leader = models.ForeignKey(Musician)
	name = models.CharField(max_length=200)
	ocode = models.CharField(max_length=30, unique=True)
	def __unicode__(self):              # __unicode__ on Python 2
		return self.name

class Recording(models.Model):
	song = models.ForeignKey(Song)
	orchestra = models.ForeignKey(Orchestra)
	label = models.ForeignKey(RecordLabel, null=True, blank=True)
	genre = models.ForeignKey(Genre)
	recorded = models.DateField(null=True, blank = True)
	discNo = models.CharField(max_length=20, null=True, blank=True)
	matrixNo = models.CharField(max_length=20, null=True, blank=True)

	def __unicode__(self):              # __unicode__ on Python 2
		return self.song.title + ' (' + self.orchestra.name + ', ' + self.recorded.strftime('%Y') + ')'

class PlayedOn(models.Model):
	musician = models.ForeignKey(Musician)
	recording = models.ForeignKey(Recording)
	role = models.ForeignKey(MusicianRole)