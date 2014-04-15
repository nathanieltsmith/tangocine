from __future__ import absolute_import

from tango_perfs.models import Performance, Performer, Couple, DanceEvent
from tango_disco.models import Recording, Song
from django.contrib.auth.models import User


from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlquote
from django.shortcuts import redirect, render
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse_lazy

from .forms import RegistrationForm, LoginForm

from braces import views
from random import shuffle
from unidecode import unidecode
import json

from django.contrib import messages


class SignUpView(views.AnonymousRequiredMixin,
				views.FormValidMessageMixin,
				generic.CreateView,
				):
	form_class = RegistrationForm
	form_valid_message = "You've successfully signed up.  Log in to continue."
	model = User
	success_url = reverse_lazy('index')
	template_name = 'tango_perfs/accounts/signup.html'

class LoginView(views.AnonymousRequiredMixin,
				views.FormValidMessageMixin,
				generic.FormView, 
				
				):
	form_class = LoginForm
	form_valid_message = "You've successfully logged in. Welcome."
	success_url = reverse_lazy('index')
	template_name = 'tango_perfs/accounts/login.html'

	def form_valid(self, form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			login(self.request, user)
			return super(LoginView, self).form_valid(form)
		else:
			return self.form_invalid(form)

class LogOutView(views.LoginRequiredMixin,
				views.MessageMixin,
				generic.RedirectView):
    url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        logout(request)
        self.messages.success("You've been logged out. Come back soon!")
        return super(LogOutView, self).get(request, *args, **kwargs)
        

def index(request):
	performer1= [request.GET.get('performer1')] if isinstance(request.GET.get('performer1'), basestring) else request.GET.getlist('performer1')
	performer2= [request.GET.get('performer2')] if isinstance(request.GET.get('performer2'), basestring) else request.GET.getlist('performer2')
	genres = [request.GET.get('genre')] if isinstance(request.GET.get('genre'), basestring) else request.GET.get('genre')
	orchestra_leaders = [request.GET.get('orc')] if isinstance(request.GET.get('orc'), basestring) else request.GET.get('orc')
	songs = [request.GET.get('song')] if isinstance(request.GET.get('song'), basestring) else request.GET.get('song')
	sort = request.GET.get('sort') if request.GET.get('sort') else '-hotness';
	latest_perf_list = Performance.objects.order_by(sort)
	total_perfs = len(latest_perf_list)
	performers = performer1+performer2
	if (performers):
		for performer in performers:
			print performer + '!!'
			if (performer):
				latest_perf_list = latest_perf_list.filter(couples__performers__simplifiedName__startswith=unidecode(performer).lower())
	if (genres):
		for genre in genres:
			if (genre):
				latest_perf_list = latest_perf_list.filter(recordings__genre__name=genre)
	if (orchestra_leaders):
		for leader in orchestra_leaders:
			if (leader):
				latest_perf_list = latest_perf_list.filter(recordings__orchestra__ocode=leader)
	if (songs):
		for song in songs:
			if (song):
				latest_perf_list = latest_perf_list.filter(recordings__song__id=song)

	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
	events = DanceEvent.objects.all().order_by('-date')
	paginator = Paginator(latest_perf_list, 20)
	page = request.GET.get('page')
	try:
		perfs = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		perfs = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		perfs = paginator.page(paginator.num_pages)
	template = loader.get_template('tango_perfs/base_feed.html')
	context = RequestContext(request, {
		'perf_list': perfs,
		'performers' : performers,
		'total_perfs' : total_perfs,
		'events' : events
	})
	return HttpResponse(template.render(context))

def prefilter(request):
	p1 = request.GET.get('performer1').replace(' ', '+') if request.GET.get('performer1') else 'all'
	p2 = request.GET.get('performer2').replace(' ', '+') if request.GET.get('performer2') else 'all'
	genre = request.GET.get('genre') if request.GET.get('genre') else 'all'
	orc = request.GET.get('orc') if request.GET.get('orc') else 'all'
	song = request.GET.get('song').replace(' ', '+') if request.GET.get('song') else 'all'
	sort = request.GET.get('sort')  if request.GET.get('sort') else '-hotness'
	return redirect('filter', performer1=p1, performer2=p2, orchestra=orc, genre=genre, sort_method=sort, song=song)
	#return HttpResponseRedirect("/filter/%s/%s/%s/%s/%s" %(p1,p2,orc,genre,sort))

def filter(request, performer1='all', performer2='all', orchestra='all', genre='all', sort_method='-hotness', song='all'):
	latest_perf_list = Performance.objects.order_by(sort_method)
	total_perfs = len(latest_perf_list)
	print performer1
	print performer2
	print orchestra
	print genre
	print sort_method
	print song
	if (performer1 != 'all'):
		latest_perf_list = latest_perf_list.filter(couples__performers__simplifiedName__icontains=unidecode(performer1).lower().replace('+', ' '))
	if (performer2 != 'all'):
		latest_perf_list = latest_perf_list.filter(couples__performers__simplifiedName__icontains=unidecode(performer2).lower().replace('+', ' '))
	if (song != 'all'):
		latest_perf_list = latest_perf_list.filter(recordings__song__simplifiedTitle=unidecode(song).lower().replace('+', ' '))
	if (genre != 'all'):
		latest_perf_list = latest_perf_list.filter(recordings__genre__name=genre)
	if (orchestra != 'all'):
		latest_perf_list = latest_perf_list.filter(recordings__orchestra__ocode=orchestra)
	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
	events = DanceEvent.objects.all().order_by('-date')
	paginator = Paginator(latest_perf_list, 20)
	page = request.GET.get('page')
	try:
		perfs = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		perfs = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		perfs = paginator.page(paginator.num_pages)
	template = loader.get_template('tango_perfs/base_feed.html')
	context = RequestContext(request, {
		'perf_list': perfs,
		'performers' : performers,
		'total_perfs' : total_perfs,
		'events' : events
	})
	return HttpResponse(template.render(context))

def addperf(request):

	rec = Recording.objects.filter(song__simplifiedTitle=unidecode(request.POST.get('song')).lower()).filter(orchestra__ocode = request.POST.get('ocode'))
	if (not rec):
		return HttpResponse("Recording not found")
	couple = getCouple(request.POST.get('lfname'), request.POST.get('llname'), request.POST.get('ffname'), request.POST.get('flname'))
	if (not couple):
		return HttpResponse("Couple creation error")
	performance = Performance(youtubeId=request.POST.get('youtubeid'), performance_type='P')
	if (request.POST.get('perf-date')):
		performance.performance_date = request.POST.get('perf-date')
	performance.save()
	performance.couples.add(couple)
	performance.recordings.add(rec[0])
	performance.save()
	return HttpResponse("Success")


# lfn = "lead first name" fln= "follow last name" etc
def getCouple(lfn, lln, ffn, fln):
	couple = Couple.objects.filter(performers__simplifiedName=unidecode(lfn + ' ' +lln).lower()).filter(performers__simplifiedName=unidecode(ffn + ' ' +fln).lower())
	if (couple):
		return couple[0]
	else:
		lead = getPerformer(lfn, lln)
		follow = getPerformer(ffn, fln)
		couple = Couple()
		couple.save()
		couple.performers.add(lead)
		couple.performers.add(follow)
		couple.save()
		return couple

def getPerformer(firstName, lastName):
	p = Performer.objects.filter(simplifiedName=unidecode(firstName+' '+lastName).lower())
	if (p):
		return p[0]
	else:
		code = firstName + lastName
		p = Performer(firstName=firstName, lastName=lastName, code=unidecode(code).lower().replace(" ", "")[:10])
		p.save()
		return p

def addPerformance(request, youtubeId=""):
	try:
		Performance.objects.get(youtubeId=youtubeId)
		return HttpResponse("This performance has already been added")
	except Exception, e:
		context = RequestContext(request, {
			'youtubeId': youtubeId,
			
		})
		template = loader.get_template('tango_perfs/add.html')
		return HttpResponse(template.render(context))

def detail(request, id):
	events = DanceEvent.objects.all().order_by('-date')
	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
	perf = Performance.objects.get(youtubeId=id)
	recording = perf.recordings.first()
	context = RequestContext(request, {
		'events' : events,
		'perf': perf,
		'performers' : performers,
	})
	template = loader.get_template('tango_perfs/detail.html')
	return HttpResponse(template.render(context))

def performer(request, performer_code):
	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
	events = DanceEvent.objects.all().order_by('-date')

	latest_perf_list = Performance.objects.filter(couples__performers__code=performer_code).order_by('hotness')
	paginator = Paginator(latest_perf_list, 10)
	page = request.GET.get('page')
	try:
		perfs = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		perfs = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		perfs = paginator.page(paginator.num_pages)
	template = loader.get_template('tango_perfs/base_feed.html')
	context = RequestContext(request, {
		'perf_list': perfs,
		'performers' : performers,
		'events' : events
	})
	return HttpResponse(template.render(context))

def event(request, event_id):
	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
	perfs = Performance.objects.filter(event__id=event_id).order_by('-totalViews')
	viewedEvent = DanceEvent.objects.get(id=event_id)
	events = DanceEvent.objects.all().order_by('-date')
	template = loader.get_template('tango_perfs/event.html')
	context = RequestContext(request, {
		'perf_list': perfs,
		'performers' : performers,
		'viewedEvent' : viewedEvent,
		'events' : events
	})
	return HttpResponse(template.render(context))

def couple(request, couple_id):
    return HttpResponse("You're looking at the page for couple %s." % couple_id)

def orchestra(request, orc_id):
    return HttpResponse("You're looking at orchestra %s." % orc_id)

def get_songs(request):
	if request.is_ajax():
		q = request.GET.get('term', '')
		songs = Song.objects.filter(simplifiedTitle__istartswith = q )[:20]
		results = []
		for song in songs:
			song_json = {}
			song_json['id'] = song.id
			song_json['label'] = song.title
			song_json['value'] = song.simplifiedTitle
			results.append(song_json)
		data = json.dumps(results)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

