from django.conf import settings
from subprocess import call
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

def itunesLookup(begin=0):
	for recording in Recording.objects.all()[begin:]:
		try:
			if (not recording.itunesLink):
				if (len(Recording.objects.filter(song=recording.song, orchestra=recording.orchestra)) == 1):
					searchTerm = recording.orchestra.leader.lastName + ' ' + ascii_lower(recording.song.title)
					searchTerm = searchTerm.replace(' ', '+')
					print searchTerm
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
										recording.itunesLink = result['trackViewUrl']
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
									if (recording.itunesId):
										if recording.itunesId == result['trackId']:
											print 'adding: '+ result['artistName'] + ' - ' + result['trackName']
											print 'for: ' + recording.orchestra.leader.lastName + ' - ' + recording.song.simplifiedTitle
											recording.itunesLink = result['trackViewUrl']
											recording.save()
											break
									# else:
									#  	if ((ascii_lower(recording.orchestra.leader.lastName) in ascii_lower(result['artistName'])) and 
									# 		(ascii_lower(recording.orchestra.leader.firstName) in ascii_lower(result['artistName']))):
									# 			if (not Song.objects.filter(simplifiedTitle=ascii_lower(result['trackName']))):
									# 				print 'found: '+ result['artistName'] + ' - ' + result['trackName']
									# 				print 'for: '+ recording.orchestra.leader.lastName + ' - ' + recording.song.simplifiedTitle
									# 				answer = raw_input('Approve?: ')
									# 				if (answer != 'n'):
									# 					recording.itunesId =  result['trackId']
									# 					recording.itunesLink = result['trackViewUrl']
									# 					recording.save()
									# 					break
								except Exception as e:
									print e
				# else:
				# 	print recording.orchestra.name + ' recorded '+ recording.song.title + ' multiple times'
				# 	for rec in Recording.objects.filter(song=recording.song, orchestra=recording.orchestra):
				# 		print rec.recorded
				# 	searchTerm = recording.orchestra.leader.lastName + ' ' + ascii_lower(recording.song.title)
				# 	searchTerm = searchTerm.replace(' ', '+')
				# 	print searchTerm
				# 	url = "https://itunes.apple.com/search?term=" + unidecode(searchTerm)
				# 	response = urllib2.urlopen(url)
				# 	jsonResp = json.loads(response.read())
				# 	print jsonResp
				# 	print "1"
				# 	if (jsonResp['resultCount'] >= 1):
				# 		print "2"
				# 		for result in jsonResp['results']:
				# 			if ((ascii_lower(recording.orchestra.leader.lastName) in ascii_lower(result['artistName'])) and 
				# 			(ascii_lower(recording.orchestra.leader.firstName) in ascii_lower(result['artistName']))):
				# 				print "3"
				# 				print 'found: '+ result['artistName'] + ' - ' + result['trackName']
				# 				print 'for: '+ recording.orchestra.leader.lastName + ' - ' + recording.song.simplifiedTitle
				# 				answer = raw_input('Approve?: ')
				# 				if (answer != 'n'):
				# 					call(["wget", result['previewUrl']])
				# 					call(["afplay", result['previewUrl'].split('/')[-1]])
				# 					raw_input('What Year?: ')
				# 					recording.itunesId =  result['trackId']
				# 					recording.save()
				# 					break
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
SEARCH_AFTER_DATE = '2014-07-15T00:00:00Z'

def youtube_search(query, pageToken=None):
	global i
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
	developerKey=DEVELOPER_KEY)
	try:
	# Call the search.list method to retrieve results associated with the
	# specified Freebase topic.
		if (pageToken):
			search_response = youtube.search().list(
				q=query,
				publishedAfter=SEARCH_AFTER_DATE,
				pageToken=pageToken,
				type='video',
				part="id,snippet",
				maxResults=50,
			).execute()
		else:
			search_response = youtube.search().list(
				q=query,
				publishedAfter=SEARCH_AFTER_DATE,
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
		print e
		time.sleep(30)
		return youtube_search(query, pageToken)

def scanDiscoVideosForLength(start=0):
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	for recording in Recording.objects.all()[start:]:
		if recording.youtubeId:
			time.sleep(.5)
			try:
				entry = client.GetYouTubeVideoEntry(video_id=recording.youtubeId)
			except Exception as e:
				print "recording not found removing"
				recording.youtubeId = ""
				recording.save()

			#print entry
			print recording.song.title +": " + entry.media.duration.seconds
			if int(entry.media.duration.seconds) > (5 *60) or int(entry.media.duration.seconds) < (2 *60):
				print "removing"
				recording.youtubeId = ""
				recording.save()

def addOffsets(start=0):
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	for recording in Recording.objects.all()[start:]:
		if recording.youtubeId:
			time.sleep(.5)
			try:
				entry = client.GetYouTubeVideoEntry(video_id=recording.youtubeId)
			except Exception as e:
				print "recording not found:"
				#recording.youtubeId = ""
				#recording.save()

			#print entry
			print recording.song.title # +": " + str(entry.author[0].name.text)
			if str(entry.author[0].name.text) == "Cantando Tangos":
				print "CT"
				recording.youtubeOffset = 4
				recording.save()
			if str(entry.author[0].name.text) == "Overjazz Records":
				print "OJ"
				recording.youtubeOffset = 4
				recording.save()


addOffsets()

def scanAllCouples(num):
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	for couple in Couple.objects.all()[num:]:
		scanCouple(couple, client)

def scanFromCouples(dancer1, dancer2):
	couple = Couple.objects.filter(performers__fullName__icontains=dancer1).filter(performers__fullName__icontains=dancer2)[0]
	num = len(Couple.objects.filter(pk__lt=couple.pk))
	scanAllCouples(num)

def scanRec(recording, client=None):
	if (not client):
		client = service.YouTubeService()
		client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	pageToken = None
	searchString = recording.song.title + ' ' + recording.orchestra.leader.lastName
	print searchString
	result = youtube_search(searchString, pageToken)
	print result
	result = result[0][0][1]
	recording.youtubeId = result
	recording.save()
	return result



def scanCouple(couple, client=None):
	print couple
	if (not client):
		client = service.YouTubeService()
		client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	names = [[x.fullName.split(' ')[0], x.lastName] for x in couple.performers.all()]
	searchStrings = []
	fullname =''
	for perf in couple.performers.all():
		fullname += perf.fullName + ' '
	searchStrings.append(fullname)
	# Check that there are not multiple couples with this name
	if len(names) > 1:
		if (len(Couple.objects.filter(performers__firstName=names[0][0]).filter(performers__firstName=names[1][0])) > 1):
			searchStrings.append(' '.join([' '.join(x) for x in names]))
		searchStrings.append(' '.join([firstName(x) for x in names]))
		for searchString in searchStrings:
			print "searching: " + searchString
			pageToken = None
			for x in range(4):
				time.sleep(1)
				print x
				result = youtube_search(searchString, pageToken)
				pageToken = result[1]
				name1 = unidecode(names[0][0]).lower()
				name2 = unidecode(names[1][0]).lower()
				filteredList = [video for video in result[0] if (name1 in video[0] and name2 in video[0])]
				for video in filteredList:
					#extractYear(video, couple, client)
					print identifyVideo(video, couple, client)

def firstName(nameArray):
	if (nameArray[0].lower() == 'el'):
		return nameArray[0]+' '+nameArray[1]
	else:
		return nameArray[0]

songBlackList = ['canaro', 'un sueno', 'el campeon','maria cristina','primer beso' 'ana maria','maria','na na', 'una vida','la final', 'en el salon', 'fresedo','te amo', 'mi vida', 'milonga', 'el tango', 'san francisco', 'la tango', 'color tango', 'buenos aires']

def extractYear(video, couple, client):
	for year in ['91', '92', '93', '94', '95', '96','97','98','99']:
		if year in video[0]:
			print video
	# largeSearch = video[0]

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
		performance = Performance(youtubeId=video[1], performance_type='P', active=False)
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

delete_bodies = ['Invalid id', 'Private video', 'Invalid request URI', 'Video not found']

def getVideoMetaData():
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	for perf in Performance.objects.filter(youtubeUploadDate=None):
		perf.previousTotalViews = int(perf.totalViews)
		try:
			time.sleep(.5)
			entry = client.GetYouTubeVideoEntry(video_id=perf.youtubeId)
			if entry.statistics:
				perf.totalViews = int(entry.statistics.view_count)
			else:
				perf.totalViews = 0
			perf.youtubeUploadDate = entry.published.text[:10]
			perf.thumbnailUrl = entry.media.thumbnail[0].url
			perf.hotness = 0
			print perf.totalViews
			perf.save()
		except Exception as e:
			print str(e) +' '+perf.youtubeId
			for delete_text in delete_bodies:
				if  delete_text in str(e):
					print 'deleting video'
					perf.delete()



def updateHotness():
	total=0
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	for perf in Performance.objects.filter(active=True):
		perf.previousTotalViews = int(perf.totalViews)
		try:
			time.sleep(.75)
			print perf.youtubeId
			entry = client.GetYouTubeVideoEntry(video_id=perf.youtubeId)
			perf.totalViews = int(entry.statistics.view_count)
			#perf.youtubeUploadDate = entry.published.text[:10]
			#perf.thumbnailUrl = entry.media.thumbnail[0].url
			perf.hotness =  (int(perf.totalViews)-int(perf.previousTotalViews))/(ceil((1.0 + int(perf.totalViews))/10000))
			total += int(perf.totalViews)-int(perf.previousTotalViews)
			print str(total) + ' ' +perf.youtubeId

			perf.save()
		except Exception as e:
			print str(e) +' '+perf.youtubeId
			# for delete_text in delete_bodies:
			# 	if  delete_text in str(e):
			# 		print 'deleting video'
			# 		perf.delete()
	return total

# client = service.YouTubeService()
# client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
# for recording in Recording.objects.all()[:5]:
# 	try:
# 		scanRec(recording, client)
# 		time.sleep(.5)
# 	except Exception as e:
# 		print "video not found"
#scanCouple(Couple.objects.get(performers__fullName__icontains='mariana montes'))
#getVideoMetaData()
#

#getVideoMetaData()
#scanFromCouples('nick', 'diana')
#scanAllCouples(0)
#getVideoMetaData()
#updateHotness()

#getVideoMetaData()
#updateHotness()
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

