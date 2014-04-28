# coding=UTF-8
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

def parseTangoInfo(url):
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html)
	song = {}
	songs = []
	for perfs in soup.find_all(class_='performance'):
		tds = [x.get_text().strip() for x in perfs.find_all('td')]
		song['title'] = tds[0]
		print song['title']
		song['genre'] = tds[2]
		print song['genre'].capitalize()
		song['singer'] = '' if (tds[4] == '-') else parseName(tds[4])
		print song['singer']
		song['date'] = tds[5]
		song['date'] = song['date'] + '-01' if len(tds[5]) ==7 else song['date']
		song['date'] = song['date'] + '-01-01' if len(tds[5]) ==4 else song['date']
		song['date'] = '' if ('--' in tds[5]) else song['date']
		print song['date']
		songs.append(song)
		song = {}
	return songs

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
		s = Song.objects.create(title = title)
		if (composer_dict):
			composer_ob = addMusician(composer_dict['first'], composer_dict['last'])
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
	po = PlayedOn.objects.filter(musician=m).filter(recording=r)
	if (not po):
		po = PlayedOn(musician=m, recording=r, role=mr)
		po.save()


def addOrchestra(first, last, name, ocode):
	if (not Orchestra.objects.filter(name = name)):
		m = addMusician(first, last)
		o = Orchestra(name=name,leader=m, ocode=ocode)
		o.save()


#parseTangoInfo('https://tango.info/performances/FrancCanar')


tangoinfoprefix = 'https://tango.info/performances/'
tangoinfoUrls = [
#('FrancCanar', u'Francisco', u'Canaro', u'Orquesta Francisco Canaro', 'canaro'),
#('xgrbrunswi', u'Orquesta Típica', u'Brunswick', u'Orquesta Típica Brunswick', 'brunswick'),
#('AdolfCarab', u'Adolfo', u'Carabelli', u'Orquesta Adolfo Carabelli', 'carabelli'),
#('FrancRotun', u'Francisco', u'Rotundo', u'Orquesta Francisco Rotundo', 'rotundo'),
#('xgrelarrnq', u'Orquesta', u'el Arranque', u'Orquesta el Arranque', 'arranque'),
#('xgjmilongu', u'Sexteto', u'Milonguero', u'Sexteto Milonguero', 'smilonguer'),
#('RoberFirpo', u'Roberto', u'Firpo', u'Orquesta Roberto Firpo', 'firpo'),
# ('JuanaDarie', u'Juan', u"D'Arienzo", u"Orquesta Juan D'Arienzo", 'darienzo'),
# ('OsvalFrese', u'Osvaldo', u'Fresedo', u'Orquesta Osvaldo Fresedo', 'fresedo'),
# ('JulioDecar', u"Julio", u"de Caro", u'Orquesta Julio de Caro', 'decaro'),
# ('FrancLomut', u'Francisco', u'Lomuto', u'Orquesta Francisco Lomuto', 'lomuto'),
# ('xgrvictora', u'Orquesta Típica', u'Víctor',u'Orquesta Típica Víctor', 'otv'),
# ('JuanfMagli', u'Juan Félix', u'Maglio', u'Orquesta Juan Maglio', 'maglio'),
# ('SalusVarel', u'Héctor', u'Varela', u'Orquesta Héctor Varela', 'varela'),
# ('EdgarDonat', u'Edgardo', u'Donato', u'Orquesta Edgardo Donato', 'donato'),
# ('ArmanPuntu', u'Armando', u'Pontier', u'Orquesta Armando Pontier', 'pontier'),
# ('MigueVilla', u'Miguel', u'Villasboas', u'Orquesta Miguel Villasboas', 'villaboas'),
# ('HoracSalga', u'Horacio', u'Salgán', u'Horacio Salgán', 'salgan'),
# ('EnriqRodri', u'Enrique', u'Rodríquez', u'Orquesta Enrique Rodríguez', 'rodriguez'),
# ('xgrcolorta', u'Color', u'Tango', u'Color Tango', 'color'),
# ('AngelDagos', u'Angel', u"D'Agostino", u"Orquesta Angel D'Agostino", 'dagostino'),
# ('PedroMaffi', u'Pedro', u'Maffia', u'Orquesta Pedro Maffia', 'maffia'),
#('AngelOrtiz', u'Ciriaco', u'Ortiz', u'Orquesta Ciriaco Ortiz', 'ortiz'),
#('xgrlsprvnc', 'Los', 'Provincianos', 'Los Provincianos', 'provincianos'),
#('HugoaDiaza', 'Hugo', "Diaz", "Hugo Diaz", 'hugodiaz'),
#('JuancCacer', 'Juan Carlos', u'Cáceres', u'Juan Carlos Cáceres', 'caceres'),
('AngelDagos', 'Angel', "D'Agostino", "Orquesta Angel D'Agostino",'dagostino')

]


for url in tangoinfoUrls:
	if (not url[4] == 'darienzo'):
		addOrchestra(url[1], url[2], url[3], url[4])
	for song in parseTangoInfo(tangoinfoprefix + url[0]):
			if (song['title']):
				try:
					s = addSong(song['title'], '','')
				
					r = addRecording(s,song['date'] ,url[3],'', '' ,song['genre'],'' )
				except Exception as e:
					print "exception: " + str(song)
				if ('singer' in song.keys() and song['singer']):
					addSinger(r, song['singer']['first'], song['singer']['last'])



letters = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split(' ')
#
orcs = [
		#("%C1ngel%20DAgostino", "12", "Angel", "D'Agostino")
		#("Osvaldo%20Pugliese", "28", "Osvaldo", "Pugliese"), 
# 		#("Rodolfo%20Biagi","104", "Rodolfo", "Biagi"), 
# 		#("Orquesta%20Miguel%20Cal%F3", "8", "Miguel", "Calo"),
# 		#("Carlos%20Di%20Sarli", "17", "Carlos", "Di Sarli"),
# 		#("Lucio%20Demare", "127", "Lucio", "Demare"),
# 		#("Jos%E9%20Garc%EDa%20y%20sus%20Zorros%20Grises", "740", "Jose", "Garcia"),
# 		#("Alfredo%20Gobbi", "21", "Alfredo", "Gobbi"),
# 		#("Pedro%20Laurenz", "22", "Pedro", "Laurenz"),
# 		#("Orquesta%20Ricardo%20Malerba", "741", "Ricardo", "Malerba"),
# 		#("Orquesta%20Ricardo%20Tanturi", "31","Ricardo", "Tanturi"),
# 		("An%EDbal%20Troilo","32","Anibal","Troilo"),
# 		#("Orquesta%20Alfredo%20De%20Angelis", "14", "Alfredo", "De Angelis")
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
