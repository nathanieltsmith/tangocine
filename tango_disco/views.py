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