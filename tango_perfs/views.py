from __future__ import absolute_import

from tango_perfs.models import Performance, Performer, Couple, DanceEvent
from tango_disco.models import Recording, Song, PlayedOn, Orchestra
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

from urllib import unquote
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
	latest_perf_list = Performance.objects.filter(active=True).order_by(sort)
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
		'events' : events,
		'trending' : True
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
	latest_perf_list = Performance.objects.filter(active=True).order_by(sort_method)
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
	newest = True if sort_method == '-created_date' else False
	trending = True if sort_method == '-hotness' else False
	personalized = True if sort_method == '?' else False
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
		'events' : events,
		'newest' : newest,
		'trending' : trending,
		'personalized' : personalized

	})
	return HttpResponse(template.render(context))

def addperf(request):

	rec = Recording.objects.filter(song__simplifiedTitle=unidecode(request.POST.get('add-song')).lower()).filter(orchestra__ocode = request.POST.get('ocode'))
	if (not rec):
		return HttpResponse("Recording not found")
	couple = getCouple(request.POST.get('add-performer1'), request.POST.get('add-performer2'))
	if (not couple):
		return HttpResponse("Couple creation error")
	performance = Performance(youtubeId=request.POST.get('youtubeid'), performance_type='P')
	if (request.POST.get('perf-date')):
		performance.performance_date = request.POST.get('perf-date')
	performance.save()
	performance.couples.add(couple)
	performance.recordings.add(rec[0])
	performance.save()
	messages.add_message(request, messages.INFO, 'Video was successfully added.  Thanks!')
	return redirect('/addform/')


# lfn = "lead first name" fln= "follow last name" etc
def getCouple(dancer1, dancer2):
	couple = Couple.objects.filter(performers__simplifiedName=unidecode(dancer1).lower()).filter(performers__simplifiedName=unidecode(dancer2).lower())
	if (couple):
		return couple[0]
	else:
		lead = getPerformer(dancer1)
		follow = getPerformer(dancer2)
		couple = Couple()
		couple.save()
		couple.performers.add(lead)
		couple.performers.add(follow)
		couple.save()
		return couple

def getPerformer(fullName):
	p = Performer.objects.filter(simplifiedName=unidecode(fullName).lower())
	if (p):
		return p[0]
	else:
		p = Performer(fullName=fullName, firstName='x', lastName='x', code=unidecode(fullName).lower().replace(" ", "")[:10])
		p.save()
		return p

def addPerformance(request, youtubeId=""):
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
	orchestras = []
	for rec in perf.recordings.all():
		print rec.orchestra.name + ' ' + rec.orchestra.ocode
		singerOb = PlayedOn.objects.filter(recording=perf.recordings.first())
		if (singerOb):
			musician = singerOb[0].musician
			singerName = musician.firstName +' '+ musician.lastName
		else:
			singerName = ""
		orchestras += [{"name":rec.orchestra.name, "code":rec.orchestra.ocode, "singer":singerName}]
	dancers = []
	for couple in perf.couples.all():
		for performer in couple.performers.all():
			dancers += [performer]
	print str(dancers)
	context = RequestContext(request, {
		'events' : events,
		'dancers': dancers,
		'perf': perf,
		'performers' : performers,
		'orchestras' : orchestras
	})
	template = loader.get_template('tango_perfs/detail.html')
	return HttpResponse(template.render(context))

def performer(request, performer_code):
	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
	events = DanceEvent.objects.all().order_by('-date')

	latest_perf_list = Performance.objects.filter(couples__performers__code=performer_code, active=True).order_by('hotness')
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
		'events' : events,
		'trending' : '1'
	})
	return HttpResponse(template.render(context))

def event(request, event_id):
	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
	perfs = Performance.objects.filter(event__id=event_id, active=True).order_by('-totalViews')
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


def get_performers(request):
	if request.is_ajax():
		q = request.GET.get('term', '')
		simplifiedName = Performer.objects.filter(simplifiedName__icontains = q )[:20]
		results = []
		print 'finished queries'
		for perf in simplifiedName:
			perf_json = {}
			perf_json['id'] = perf.code
			perf_json['label'] = perf.fullName
			perf_json['value'] = perf.fullName
			results.append(perf_json)
		data = json.dumps(results)
		print data
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

def get_orchestras(request):
	#if request.is_ajax():
	song = Song.objects.get(simplifiedTitle=unquote(request.GET.get('song', '')))
	orchestras = []
	for rec in Recording.objects.filter(song=song):
		orc_dict = {'title': rec.orchestra.name, 'value': rec.orchestra.ocode}
		if orc_dict not in orchestras:
			orchestras.append(orc_dict)
	data = json.dumps(orchestras)
	#else:
	#	data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

def get_years(request):
	#if request.is_ajax():
	song = Song.objects.get(simplifiedTitle=request.GET.get('song', ''))
	orchestra = Orchestra.objects.get(ocode=request.GET.get('orc', ''))
	years = []
	for rec in Recording.objects.filter(song=song, orchestra=orchestra).order_by('recorded'):
		if rec.recorded:
			year_dict = {"title": rec.recorded.strftime('%Y'), "value": rec.recorded.strftime('%Y')}
			if year_dict not in years:
				years.append(year_dict)
		else:
			years.append({"title": "year unknown", "value":"unknown"})
	data = json.dumps(years)
	#else:
	#	data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

def video_added(request, youtubeId):
	mimetype = 'application/json'
	try:
		Performance.objects.get(youtubeId=youtubeId);
		return HttpResponse(json.dumps(['success']), mimetype)
	except Exception as e:
		return HttpResponse(json.dumps(['failure']), mimetype)

	

		