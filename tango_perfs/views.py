from django.shortcuts import render
from tango_perfs.models import Performance, Performer, Couple
from tango_disco.models import Recording
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from random import shuffle

# Create your views here.
from django.http import HttpResponse

def index(request):
	latest_perf_list = Performance.objects.order_by('-created_date')
	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]
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
	template = loader.get_template('tango_perfs/index.html')
	context = RequestContext(request, {
		'latest_perf_list': perfs,
		'performers' : performers
	})
	return HttpResponse(template.render(context))

def addperf(request):
	rec = Recording.objects.filter(song__title=request.POST.get('song')).filter(orchestra__ocode = request.POST.get('ocode'))
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
	couple = Couple.objects.filter(performers__firstName=lfn).filter(performers__firstName=ffn).filter(performers__lastName=lln).filter(performers__lastName=fln)
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
	p = Performer.objects.filter(firstName=firstName).filter(lastName=lastName)
	if (p):
		return p[0]
	else:
		code = firstName.replace(" ", "") + lastName[0]
		p = Performer(firstName=firstName, lastName=lastName, code=code.lower()[:10])
		p.save()
		return p



def detail(request, perf_id):
    return HttpResponse("You're looking at performance # %s." % perf_id)

def performer(request, performer_code):
	performers = Performer.objects.exclude(lastName="????").order_by('?')[:20]

	latest_perf_list = Performance.objects.filter(couples__performers__code=performer_code).order_by('-created_date')
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
	template = loader.get_template('tango_perfs/index.html')
	context = RequestContext(request, {
		'latest_perf_list': perfs,
		'performers' : performers
	})
	return HttpResponse(template.render(context))

def couple(request, couple_id):
    return HttpResponse("You're looking at the page for couple %s." % couple_id)

def orchestra(request, orc_id):
    return HttpResponse("You're looking at orchestra %s." % orc_id)

