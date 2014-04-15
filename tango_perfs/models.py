from django.db import models
from tango_disco.models import Recording
from unidecode import unidecode
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from tango_disco.models import Song, Recording, Orchestra
import time


import json
import urllib

DEVELOPER_KEY = "AIzaSyDrA7m_-GdUADsKq2bmwMhQlMNbIDSQpcU"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Create your models here.
class Performer(models.Model):
	firstName = models.CharField(max_length=30)
	lastName = models.CharField(max_length=30)
	simplifiedName = models.CharField(max_length=60, null=True, blank=True)
	code = models.CharField(max_length=10, null=True, blank=True, unique=True)

	def __unicode__(self):              # __unicode__ on Python 2
		return self.firstName +' '+ self.lastName

	def merge(self, performer):
		for couple in Couple.objects.filter(performers=performer):
			couple.performers.remove(performer)
			couple.performers.add(self)
			couple.save()
			performer.delete()

	def numPerfs(self):
		return len(Performance.objects.filter(couples__performers=self))

	def listPartners(self):
		partners = ''
		for couple in Couple.objects.filter(performers=self):
			for perf in couple.performers.all():
				if (perf != self):
					partners += perf.firstName + ' ' + perf.lastName +', '
		return partners[:-2]

	def save(self, *args, **kwargs):
		self.simplifiedName = unidecode(self.firstName + ' ' + self.lastName).lower()
		super(Performer, self).save(*args, **kwargs) # Call the "real" save() method.


class Couple(models.Model):
	performers = models.ManyToManyField(Performer)
	def __unicode__(self):              # __unicode__ on Python 2
		try: 
			if self.performers.first().lastName == self.performers.last().lastName:
				return self.performers.first().firstName+ ' and ' + self.performers.last().firstName + ' '+ self.performers.first().lastName
			else:
				return self.performers.first().firstName+ ' '+ self.performers.first().lastName+ ' and ' + self.performers.last().firstName + ' '+ self.performers.last().lastName
		except:
			return 'blah'

	def scanForVideos(self):
		names = [[x.firstName, x.lastName] for x in self.performers.all()]
		print names
		if (len(Couple.objects.filter(performers__firstName=names[0][0]).filter(performers__firstName=names[1][0])) > 1):
			searchString = ' '.join([' '.join(x) for x in names])
		else:
			searchString = ' '.join([x[0] for x in names])
		pageToken = None
		for x in range(5):
			result = self.youtube_search(searchString, pageToken)
			pageToken = result[1]
			name1 = unidecode(names[0][0]).lower()
			name2 = unidecode(names[1][0]).lower()
			filteredList = [video for video in result[0] if (name1 in video[0] and name2 in video[0])]
			for video in filteredList:
				print self.identifyVideo(video)

	def identifyVideo(self, video):
		if (not Performance.objects.filter(youtubeId=video[1])):
			print 'searching: ' +video[0]
			for orc in Orchestra.objects.all():
				print "looking for orchestra: " + unidecode(orc.name).lower()
				print "also searching: " + unidecode(orc.leader.lastName).lower()
				if ((unidecode(orc.name).lower() in video[0]) or (unidecode(orc.leader.lastName).lower() in video[0])):
					print 'found orchestra: ' + orc.name
					for recording in Recording.objects.filter(orchestra=orc):
						if (unidecode(recording.song.title).lower() in video[0]):
							performance = Performance(youtubeId=video[1], performance_type='P')
							performance.save()
							performance.couples.add(self)
							performance.recordings.add(recording)
							performance.save()
							return 'success '
			return 'performance not found :('

	def youtube_search(self, query, pageToken=None):
		global i
		youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
		developerKey=DEVELOPER_KEY)
		try:
		# Call the search.list method to retrieve results associated with the
		# specified Freebase topic.
			if (pageToken):
				search_response = youtube.search().list(
					pageToken=pageToken,
					type='video',
					part="id,snippet",
					maxResults=50,
				).execute()
			else:
				search_response = youtube.search().list(
					q=query,
					type='video',
					part="id,snippet",
					maxResults=50,
					
				).execute()
		
			newPageToken = search_response.get('nextPageToken',[])
			# Print the title and ID of each matching resource.
			searchResults = [(unidecode(search_result["snippet"]["title"]+ ' ' +search_result["snippet"]["description"]).lower(), search_result["id"]["videoId"]) for search_result in search_response.get("items", [])]
			return (searchResults, newPageToken)
		except Exception:
			print 'Google sucks, retrying in 30 seconds'
			time.sleep(30)
			return youtube_search(query, pageToken)

	def save(self, *args, **kwargs):
		super(Couple, self).save(*args, **kwargs) # Call the "real" save() method.
		#if(len(self.performers.all()) > 1):
		#	self.scanForVideos()

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
	youtubeId = models.CharField(max_length=30, unique=True)
	thumbnailUrl = models.CharField(max_length=100, default="http://terryshoemaker.files.wordpress.com/2013/03/placeholder1.jpg")
	totalViews = models.IntegerField(default=0)
	previousTotalViews = models.IntegerField(default=0)
	hotness = models.IntegerField(default=0)
	event = models.ForeignKey(DanceEvent, null=True, blank=True)
	performance_type = models.CharField(max_length=1, choices=PERFORMANCE_TYPES)
	performance_date = models.DateField(null=True, blank=True)
	youtubeUploadDate = models.DateField(null=True, blank=True)
	created_date = models.DateTimeField(auto_now_add=True, editable=False)
	def __unicode__(self):
		try:
			return self.couples.first().__unicode__() + ': ' + self.recordings.first().__unicode__()
		except Exception:
			return 'error'  
	def save(self, *args, **kwargs):
		self.thumbnailUrl = "https://i1.ytimg.com/vi/"+ self.youtubeId+"/0.jpg"
		super(Performance, self).save(*args, **kwargs) # Call the "real" save() method.
		#if(len(self.performers.all()) > 1):
		#	self.scanForVideos()

