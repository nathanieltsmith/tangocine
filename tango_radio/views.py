from __future__ import absolute_import
from django.contrib.auth.models import User
from django.conf import settings
from .models import Tanda
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlquote
from django.shortcuts import redirect, render
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q

from tango_disco.models import Recording

from endless_pagination.decorators import page_template

from urllib import unquote
from braces import views
from random import shuffle
from unidecode import unidecode
import json

from django.contrib import messages

from apiclient.discovery import build
from apiclient.errors import HttpError
from gdata.youtube import service


# Create your views here.
def radio(request):
	# DEVELOPER_KEY = settings.GOOGLE_DEVELOPER_KEY
	# YOUTUBE_API_SERVICE_NAME = "youtube"
	# YOUTUBE_API_VERSION = "v3"
	# youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
	# 	developerKey=DEVELOPER_KEY)
	# playlists_insert_response = youtube.playlists().insert(
	# 	part="snippet,status",
	# 	body=dict(
	# 		snippet=dict(
	# 			title="Test Playlist",
	# 			description="A private playlist created with the YouTube API v3"
	# 		),
	# 		status=dict(
	# 			privacyStatus="private"
	# 		)
	# 	)
	# ).execute()
	
	client = service.YouTubeService()
	client.ClientLogin(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
	client.developer_key = settings.GOOGLE_DEVELOPER_KEY
	playlists_insert_response = client.AddPlaylist('Custom Playlist', 'http://www.tangocine.com/radio/tanda')
	playlist_id = playlists_insert_response.id.text.split('/')[-1]
	tandas = Tanda.objects.all().order_by('?')[:3]
	first_song = None
	for tanda in tandas:
		if not first_song:
			first_song = tanda.firstSong.youtubeId
		client.AddPlaylistVideoEntryToPlaylist(playlist_uri='http://gdata.youtube.com/feeds/api/playlists/'+playlist_id, video_id=tanda.firstSong.youtubeId)
		client.AddPlaylistVideoEntryToPlaylist(playlist_uri='http://gdata.youtube.com/feeds/api/playlists/'+playlist_id, video_id=tanda.secondSong.youtubeId)
		client.AddPlaylistVideoEntryToPlaylist(playlist_uri='http://gdata.youtube.com/feeds/api/playlists/'+playlist_id, video_id=tanda.thirdSong.youtubeId)
		client.AddPlaylistVideoEntryToPlaylist(playlist_uri='http://gdata.youtube.com/feeds/api/playlists/'+playlist_id, video_id=tanda.fourthSong.youtubeId)
	template = loader.get_template('radio.html')
	context = RequestContext(request, {
		'playlist_id' : playlist_id,
		'first_song' : first_song
	})
	return HttpResponse(template.render(context))

def add_tanda(request):
	if request.method == 'POST':
		songs = []
		suffixes = ['-1', '-2', '-3', '-4']
		for suffix in suffixes: 
			song = request.POST.get('add-song'+ suffix)
			orc = request.POST.get('ocode'+ suffix)
			year = request.POST.get('year'+ suffix)
			songs.append(Recording.objects.filter(song__simplifiedTitle=song, orchestra__ocode=orc, recorded__year=year)[0])
		tanda = Tanda(firstSong=songs[0], secondSong=songs[1], thirdSong=songs[2], fourthSong=songs[3], createdby=request.user)
		tanda.save()
	template = loader.get_template('addtanda.html')
	context = RequestContext(request, {
		'test' : 'test'
	})
	return HttpResponse(template.render(context))

def get_tanda(request):
	tanda = Tanda.objects.all().order_by('?')[0]
	response = [tanda.firstSong.youtubeId, tanda.secondSong.youtubeId, tanda.thirdSong.youtubeId, tanda.fourthSong.youtubeId]
	data = json.dumps(response)
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

def radio_recordings(request):
	tandas = Tanda.objects.all()
	recs = []
	for tanda in tandas:
		recs = recs + [tanda.firstSong, tanda.secondSong, tanda.thirdSong, tanda.fourthSong]
	context = RequestContext(request, {
		'recordings' : recs
	})
	template = loader.get_template('list_recordings.html')
	return HttpResponse(template.render(context))
