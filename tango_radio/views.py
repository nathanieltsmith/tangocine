from __future__ import absolute_import
from django.contrib.auth.models import User
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


# Create your views here.
def radio(request):
	template = loader.get_template('radio.html')
	context = RequestContext(request, {
		'test' : 'test'
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