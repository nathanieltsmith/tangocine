import urllib2
import re
import time

from bs4 import BeautifulSoup
from tango_disco.models import Song, Genre, Musician, Orchestra, Recording, PlayedOn, RecordLabel, MusicianRole

import os
url = 'http://www.todotango.com/english/biblioteca/discografias/grabaciones_autor.asp?id=%s&c=%s&NAV=%s&fid=&t=&psize=10&letra=%s'
def parseName(name):
	newName = name.strip()
	nameDict = {}
	nameDict['last'] = newName.split(' ')[-1]
	nameDict['first'] = ' '.join(newName.split(' ')[:-1])
	return nameDict

def parseTodoDisco(url):
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html)
	#print soup.prettify()
	songs = []
	song = {}
	for titles in soup.find_all('span'):
		
		#print titles['class']
		if ('texto' in titles['class'] ):
			song['title'] = titles.get_text().strip()
		if ('textog' in titles['class'] ):
			text = titles.get_text().split('\n')
			song['genre'] =  text[0].strip()
			authors = text[1].strip()
			if (u'- Lyric:' in authors):
				authors, song['lyrics'] = authors.split(u'- Lyric:')
			song['composer'] = authors.replace('Music:', '').strip()

			song['orchestra'] = text[2].strip()
			data = text[3].strip()
			date = text[4].strip()
			if (u'Matrix:' in data):
				data, song['matrix'] = data.split(u'Matrix:')
			if (u'Disc:' in data):
				data, song['disc'] = data.split(u'Disc:')
			if (u'Company:' in data):
				data, song['label'] = data.split(u'Company:')
			song['singer'] = data.replace('Singer:', '').strip()

			if len(date) > 15:
				date_array = date[6:-2].split(u'/')
				day = u'0'+ date_array[1] if len(date_array[1]) == 1 else  date_array[1]
				month = u'0'+ date_array[0] if len(date_array[0]) == 1 else  date_array[0]
				year = date_array[2]
				song['date'] = '%s-%s-%s' % (year, month, day)
			else:
				song['date'] = date[7:]+'-01-01'
			nameFields = ['lyrics', 'composer', 'singer']
			for field in nameFields:
				if field in song.keys():
					song[field] = parseName(song[field])
			songs.append(song)
			song = {}
	return songs

def addSong(title, composer_dict, lyricist_dict):
	s = Song.objects.filter(title=title)
	if (s):
		#print 'song found: ' + title
		return s[0]
	else:
		print 'no song found - creating '+ title
		composer_ob = addMusician(composer_dict['first'], composer_dict['last'])
	
		s = Song.objects.create(title = title)
		s.composer = [composer_ob]
		if (lyricist_dict):
			lyricist_ob = addMusician(lyricist['firstName'], lyricist['lastName'])
			s.lyricist = [lyricist_ob]
		s.save()
		return s

def addMusician(firstName, lastName):
	m = Musician.objects.filter(firstName = firstName).filter(lastName=lastName)
	if (m):
		#print 'musician found: ' + firstName + ' ' + lastName
		return m[0]
	else:
		print 'creating musician: ' + firstName + ' ' + lastName
		m = Musician(firstName=firstName, lastName=lastName)
		m.save()
		return m

def addRecording(song, date, orchestra, matrix, disc, genre, label):
	r = Recording.objects.filter(song__title = song.title).filter(recorded=date)
	o = Orchestra.objects.filter(name = orchestra)[0]
	l = RecordLabel.objects.filter(name=label)
	g = Genre.objects.filter(name=genre)
	if (not g):
		print "Creating new Genre " + genre
		g = Genre(name=genre)
		g.save()
	else:
		g = g[0]
	if (not l):
		print "Creating new Record Label " + label
		l = RecordLabel(name=label)
		l.save()
	else:
		l = l[0]
	if (r):
		#print 'recording already exists: '+ song.title
		return r[0]
	else:
		print 'creating recording: ' + song.title + ', ' + orchestra + ', ' + date
		r = Recording(song=song, orchestra=o, label=l, genre=g, recorded = date, discNo=disc, matrixNo=matrix )
		r.save()
		return r

	# nameFields = ['lyrics', 'composer', 'singer']
	# 	for field in nameFields:
	# 		if field in disco_entry.keys():

	#Does the song exist?  If not, add it

def addSinger(r, first, last):
	#print 'adding singer %s %s' % (first, last)
	m = addMusician(first, last)
	mr = MusicianRole.objects.filter(name='singer')
	if (mr):
		mr = mr[0]
	else:
		mr = MusicianRole(name='singer')
		mr.save()
	po = PlayedOn(musician=m, recording=r, role=mr)
	po.save()


def addOrchestra(first, last, name, ocode):
	if (not Orchestra.objects.filter(name = name)):
		m = addMusician(first, last)
		o = Orchestra(name=name,leader=m, ocode=ocode)
		o.save()

letters = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split(' ')
#letters = "O".split(' ')
orcs = [#("Osvaldo%20Pugliese", "28", "Osvaldo", "Pugliese"), 
		#("Rodolfo%20Biagi","104", "Rodolfo", "Biagi"), 
		#("Orquesta%20Miguel%20Cal%F3", "8", "Miguel", "Calo"),
		#("Carlos%20Di%20Sarli", "17", "Carlos", "Di Sarli"),
		#("Lucio%20Demare", "127", "Lucio", "Demare"),
		#("Jos%E9%20Garc%EDa%20y%20sus%20Zorros%20Grises", "740", "Jose", "Garcia"),
		#("Alfredo%20Gobbi", "21", "Alfredo", "Gobbi"),
		#("Pedro%20Laurenz", "22", "Pedro", "Laurenz"),
		#("Orquesta%20Ricardo%20Malerba", "741", "Ricardo", "Malerba"),
		#("Orquesta%20Ricardo%20Tanturi", "31","Ricardo", "Tanturi"),
		("An%EDbal%20Troilo","32","Anibal","Troilo"),
		#("Orquesta%20Alfredo%20De%20Angelis", "14", "Alfredo", "De Angelis")
		]
ocode = 1
for orc in orcs:
	for letter in letters:
		for nav in range(1, 21):
			#time.sleep(5)
			for song in parseTodoDisco(url % (orc[1],orc[0],nav,letter)):
				addOrchestra(orc[2], orc[3], song['orchestra'], str(ocode))
				ocode += 1
				lyricista = song['lyricist'] if 'lyricist' in song.keys()  else {}
				s = addSong(song['title'], song['composer'], lyricista)
				mat = '' if not 'matrix'in song.keys() else song['matrix'] 
				lab = '' if not 'label' in song.keys() else song['label']
				disc = ''  if not 'disc' in song.keys() else song['disc']
				try:
					r = addRecording(s,song['date'] ,song['orchestra'],mat, disc ,song['genre'],lab )
				except Exception as e:
					print "exception: " + str(song)
				if ('singer' in song.keys() and (song['singer']['last'] != 'Instrumental')):
					addSinger(r, song['singer']['first'], song['singer']['last'])
