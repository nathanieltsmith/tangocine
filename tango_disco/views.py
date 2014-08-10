from __future__ import absolute_import
from django.contrib.auth.models import User

from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlquote
from django.shortcuts import redirect, render
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q

from endless_pagination.decorators import page_template

from urllib import unquote
from braces import views
from random import shuffle
from unidecode import unidecode
import json

from django.contrib import messages


# Create your views here.
def radio(request):
	template = loader.get_template('radio.html')
	context = RequestContext(request, {
		'test' : 'test'
	})
	return HttpResponse(template.render(context))

def update_youtube(request):
#if request.is_ajax():
	try:
		song = Recording.objects.get(pk=request.GET.get('recording', ''))
		youtubeId = request.GET.get('youtube_id', '')
		song.youtubeId = youtubeId
		song.save()
		result = "success" 
	except Exception e:
		result = "failure"
	data = json.dumps([result])
	#else:
	#	data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

def index(request):
	page_template = 'tango_perfs/base_feed_page.html'
	genres = [request.GET.get('genre')] if isinstance(request.GET.get('genre'), basestring) else request.GET.get('genre')
	orchestra_leaders = [request.GET.get('orc')] if isinstance(request.GET.get('orc'), basestring) else request.GET.get('orc')
	songs = [request.GET.get('song')] if isinstance(request.GET.get('song'), basestring) else request.GET.get('song')
	start_year = [request.GET.get('start')] if isinstance(request.GET.get('start'), basestring) else request.GET.get('start')
	end_year = [request.GET.get('end')] if isinstance(request.GET.get('end'), basestring) else request.GET.get('end')

	recordings = Recording.objects.all().order_by(recorded)
	
	if (genres):
		for genre in genres:
			if (genre):
				recordings = recordings.filter(genre__name=genre)
	if (orchestra_leaders):
		for leader in orchestra_leaders:
			if (leader):
				recordings = recordings.filter(orchestra__ocode=leader)
	if (songs):
		for song in songs:
			if (song):
				recordings = recordings.filter(recordings__song__id=song)



	#performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
	#events = DanceEvent.objects.all().order_by('-date')
	# paginator = Paginator(latest_perf_list, 20)
	# page = request.GET.get('page')
	# try:
	# 	perfs = paginator.page(page)
	# except PageNotAnInteger:
	# 	# If page is not an integer, deliver first page.
	# 	perfs = paginator.page(1)
	# except EmptyPage:
	# 	# If page is out of range (e.g. 9999), deliver last page of results.
	# 	perfs = paginator.page(paginator.num_pages)
	template = loader.get_template('recordings.html')

	context = RequestContext(request, {
		'recordings' : recordings
	})
	return HttpResponse(template.render(context))