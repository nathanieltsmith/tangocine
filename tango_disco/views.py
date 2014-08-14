from __future__ import absolute_import
from django.contrib.auth.models import User

from tango_disco.models import Recording, Song, PlayedOn, Orchestra

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
	except Exception as e:
		result = "failure"
	data = json.dumps([result])
	#else:
	#	data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

def index(request):
	page_template = 'tango_perfs/base_feed_page.html'
	genres = [request.POST.get('genre')] if isinstance(request.POST.get('genre'), basestring) else request.POST.get('genre')
	orchestra_leaders = [request.POST.get('orc')] if isinstance(request.POST.get('orc'), basestring) else request.POST.get('orc')
	songs = [request.POST.get('song')] if isinstance(request.POST.get('song'), basestring) else request.POST.get('song')
	singer = [request.POST.get('singer')] if isinstance(request.POST.get('singer'), basestring) else request.POST.get('singer')
	start_year = [request.POST.get('starting-year')] if isinstance(request.POST.get('starting-year'), basestring) else request.POST.get('starting-year')
	end_year = [request.POST.get('ending-year')] if isinstance(request.POST.get('ending-year'), basestring) else request.POST.get('ending-year')

	recordings = Recording.objects.select_related('genre__name').filter(recorded__gt='1927-01-01').filter(recorded__lt='1959-01-01').order_by('recorded')
	if (start_year and start_year[0]):
		recordings = recordings.filter(recorded__gt=start_year[0]+'-01-01')
	if (end_year and end_year[0]):
		recordings = recordings.filter(recorded__lt=end_year[0]+'-12-31')
	if (singer and singer[0]):
		recordings = recordings.filter(singer__icontains=singer[0])
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
				recordings = recordings.filter(song__title__icontains=song)



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
	firstVideo = recordings[0].youtubeId
	template = loader.get_template('recordings.html')

	context = RequestContext(request, {
		'recordings' : recordings[:200],
		'firstVideo' : firstVideo
	})
	return HttpResponse(template.render(context))