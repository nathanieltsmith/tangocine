from django.conf import settings

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from tango_perfs.models import Couple, Performance
from tango_disco.models import Song, Recording, Orchestra
from unidecode import unidecode
import time
from gdata.youtube import service
from math import ceil
import urllib2

import json
import urllib

def itunesLookup():
	for recording in Recording.objects.all():
		try:
			if (not recording.itunesId):
				if (len(Recording.objects.filter(song=recording.song, orchestra=recording.orchestra)) == 1):
					searchTerm = recording.orchestra.leader.lastName + ' ' + ascii_lower(recording.song.title)
					searchTerm = searchTerm.replace(' ', '+')
					#print searchTerm
					url = "https://itunes.apple.com/search?term=" + unidecode(searchTerm)
					response = urllib2.urlopen(url)
					jsonResp = json.loads(response.read())
					found = False
					if (jsonResp['resultCount'] >= 1):
						for result in jsonResp['results']:
							try: 
								if ((ascii_lower(recording.orchestra.leader.lastName) in ascii_lower(result['artistName'])) and 
									(ascii_lower(recording.orchestra.leader.firstName) in ascii_lower(result['artistName']))):
									if (ascii_lower(result['trackName']) in recording.song.simplifiedTitle and
										recording.song.simplifiedTitle in (ascii_lower(result['trackName']))):
										recording.itunesId = result['trackId']
										recording.save()
										print 'adding: '+ result['artistName'] + ' - ' + result['trackName']
										print 'for: ' + recording.orchestra.leader.lastName + ' - ' + recording.song.simplifiedTitle
										found = True
										break
							except Exception as e:
								print e
						if (not found):
							for result in jsonResp['results']:
								try:
									if ((ascii_lower(recording.orchestra.leader.lastName) in ascii_lower(result['artistName'])) and 
									(ascii_lower(recording.orchestra.leader.firstName) in ascii_lower(result['artistName']))):
										if (not Song.objects.filter(simplifiedTitle=ascii_lower(result['trackName']))):
											print 'found: '+ result['artistName'] + ' - ' + result['trackName']
											print 'for: '+ recording.orchestra.leader.lastName + ' - ' + recording.song.simplifiedTitle
											answer = raw_input('Approve?: ')
											if (answer != 'n'):
												recording.itunesId =  result['trackId']
												recording.save()
												break
								except Exception as e:
									print e
				else:
					print recording.orchestra.name + ' recorded '+ recording.song.title + ' multiple times'
			else:
				print recording.orchestra.name + ' '+ recording.song.title + ' id already exists'
		except Exception as e:
			print e


def ascii_lower(text):
	#print text 
	return unidecode(text).lower()


#itunesLookup()

# get the couple object for the performers in question
# do a youtube search for the couple's name
# for each video
i = 0
DEVELOPER_KEY = settings.GOOGLE_DEVELOPER_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(query, pageToken=None):
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
	except Exception as e:
		print 'Google sucks, retrying in 30 seconds'
		time.sleep(30)
		return youtube_search(query, pageToken)



def scanAllCouples(num):
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	for couple in Couple.objects.all()[num:]:
		scanCouple(couple, client)


def scanCouple(couple, client=None):
	if (not client):
		client = service.YouTubeService()
		client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	names = [[x.fullName.split(' ')[0], x.lastName] for x in couple.performers.all()]
	searchStrings = []
	# Check that there are not multiple couples with this name
	if (len(Couple.objects.filter(performers__firstName=names[0][0]).filter(performers__firstName=names[1][0])) > 1):
		searchStrings.append(' '.join([' '.join(x) for x in names]))
	searchStrings.append(' '.join([x[0] for x in names]))
	for searchString in searchStrings:
		pageToken = None
		for x in range(7):
			time.sleep(1)
			result = youtube_search(searchString, pageToken)
			pageToken = result[1]
			name1 = unidecode(names[0][0]).lower()
			name2 = unidecode(names[1][0]).lower()
			filteredList = [video for video in result[0] if (name1 in video[0] and name2 in video[0])]
			for video in filteredList:
				print identifyVideo(video, couple, client)

songBlackList = ['canaro', 'un sueno', 'el campeon','maria cristina','primer beso' 'ana maria','maria','na na', 'una vida','la final', 'en el salon', 'fresedo','te amo', 'mi vida', 'milonga', 'el tango', 'san francisco', 'la tango', 'color tango', 'buenos aires']

def identifyVideo(video, scanCouple, client):
	if (not Performance.objects.filter(youtubeId=video[1])):
		largeSearch = video[0]
		# try:
		# 	for comment in comments_generator(client, video[1]):
		# 		if (comment.content.text):
		# 			largeSearch += ' ' + comment.content.text
		# except Exception:
		# 	print 'comments unreadable'
		for orc in Orchestra.objects.all():
			if ((unidecode(orc.name).lower() in largeSearch) or (unidecode(orc.leader.lastName).lower() in largeSearch)):
				for recording in Recording.objects.filter(orchestra=orc):
					if (unidecode(recording.song.title).lower() in largeSearch
					 and (not unidecode(recording.song.title).lower() in songBlackList)
					 and (len(recording.song.title.split()) > 2)):
						performance = Performance(youtubeId=video[1], performance_type='P')
						performance.save()
						performance.couples.add(scanCouple)
						performance.recordings.add(recording)
						performance.save()
						return str(performance)
				for recording in Recording.objects.filter(orchestra=orc):
					if (unidecode(recording.song.title).lower() in largeSearch
					 and (not unidecode(recording.song.title).lower() in songBlackList)
					 and (len(recording.song.title.split()) > 1)):
						performance = Performance(youtubeId=video[1], performance_type='P')
						performance.save()
						performance.couples.add(scanCouple)
						performance.recordings.add(recording)
						performance.save()
						return str(performance)
				for recording in Recording.objects.filter(orchestra=orc):
					if (unidecode(recording.song.title).lower() in largeSearch
					 and (not unidecode(recording.song.title).lower() in songBlackList)):
						performance = Performance(youtubeId=video[1], performance_type='P')
						performance.save()
						performance.couples.add(scanCouple)
						performance.recordings.add(recording)
						performance.save()
						return str(performance)
		performance = Performance(youtubeId=video[1], performance_type='P')
		performance.save()
		performance.couples.add(scanCouple)
		performance.recordings.add(Recording.objects.get(song__title="Unknown Song"))
		performance.save()
		return str(performance)
		# for song in Song.objects.all():
		# 	simpTitle = unidecode(song.title).lower()
		# 	if (len(simpTitle.split()) > 1 and (not simpTitle in songBlackList)):
		# 		if (unidecode(song.title).lower() in video[0]):
		# 			recs = Recording.objects.filter(song=song)
		# 			if (len(recs)==1):
		# 				performance = Performance(youtubeId=video[1], performance_type='P')
		# 				performance.save()
		# 				performance.couples.add(scanCouple)
		# 				performance.recordings.add(recs[0])
		# 				performance.save()
		# 				return str(performance)
	return 'performance already added :('


def comments_generator(client, video_id):
    comment_feed = client.GetYouTubeVideoCommentFeed(video_id=video_id)
    while comment_feed is not None:
        for comment in comment_feed.entry:
             yield comment
        next_link = comment_feed.GetNextLink()
        if next_link is None:
             comment_feed = None
        else:
             comment_feed = client.GetYouTubeVideoCommentFeed(next_link.href)

# client = service.YouTubeService()
# client.ClientLogin('nathanieltsmith@gmail.com', 'mi-42gak35')

# for comment in comments_generator(client, 'dJCJ7QWx5KE'):
#     author_name = comment.author[0].name.text
#     text = comment.content.text
#     print("{}: {}".format(author_name, text))

def getVideoMetaData():
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	for perf in Performance.objects.filter(youtubeUploadDate=None):
		perf.previousTotalViews = int(perf.totalViews)
		try:
			time.sleep(1)
			entry = client.GetYouTubeVideoEntry(video_id=perf.youtubeId)
			perf.totalViews = int(entry.statistics.view_count)
			perf.youtubeUploadDate = entry.published.text[:10]
			perf.thumbnailUrl = entry.media.thumbnail[0].url
			perf.hotness = 0
			print perf.totalViews
			perf.save()
		except Exception as e:
			print str(e)


def updateHotness():
	total=0
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	for perf in Performance.objects.filter(active=True):
		perf.previousTotalViews = int(perf.totalViews)
		try:
			time.sleep(1)
			entry = client.GetYouTubeVideoEntry(video_id=perf.youtubeId)
			perf.totalViews = int(entry.statistics.view_count)
			#perf.youtubeUploadDate = entry.published.text[:10]
			#perf.thumbnailUrl = entry.media.thumbnail[0].url
			perf.hotness =  (int(perf.totalViews)-int(perf.previousTotalViews))/(ceil((1.0 + int(perf.totalViews))/10000))
			total += int(perf.totalViews)-int(perf.previousTotalViews)
			print total
			perf.save()
		except Exception as e:
			print str(e)
	return total



scanAllCouples(0)
getVideoMetaData()
updateHotness()
# def scanVideo(videoText)
# if the video is not already in the database
# 	convert accents and make the text lower case in the title and details
# 	if both performers first names are in the text:
# 	for each orchestra:
# 		if the orchestra leader's last name or the the orchestra name is found in the text
# 			for each recording of the orchestra:
# 				if the song title is in the text
# 					create a performance object
# 	for each song:
# 		if the song is in the text
# 			get a list of all recordings of the song
# 			if there's only one
# 				return a performance object
# 			else:
# 				print youtubeId, song, possible orchestras
# 				return None
# 	return None

