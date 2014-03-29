import urllib2
import re
import time

from bs4 import BeautifulSoup
from tango_disco.models import Song, Genre, Musician, Orchestra, Recording, PlayedOn, RecordLabel, MusicianRole

PugLetters = "A B C D E F G H I J L M N O P Q R S T U V W Y Z".split(' ')
url = 'http://www.todotango.com/english/biblioteca/discografias/grabaciones_autor.asp?id=28&c=Osvaldo%20Pugliese&letra='

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

	for titles in soup.find_all('span'):
		song = {}
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
	return songs

def addSong(title, composer_dict, lyricist_dict):
	s = Song.objects.filter(title=title).filter(composer__lastName=composer[lastName])
	if (s):
		print 'song found: ' + title
		return s[0]
	else:
		print 'no song found - creating '+ title
		composer_ob = addMusician(composer['firstName'], composer['lastName'])
		if (lyricist_dict):
			lyricist_ob = addMusician(lyricist['firstName'], lyricist['lastName'])
			s.lyricist = lyricist_ob
		else:
			s = Song(title = title, composer=composer_ob)
		s.save
		return s

def addMusician(firstName, lastName):
	m = Musician.objects.filter(firstName = firstName).filter(lastName=lastName)
	if (m):
		print 'musician found: ' + firstName + ' ' + lastName
		return m[0]
	else:
		print 'creating musician: ' + firstName + ' ' + lastName
		m = Musician(firstName=firstName, lastName=lastName)
		m.save()
		return m

#def addRecording(disco_entry):

	# nameFields = ['lyrics', 'composer', 'singer']
	# 	for field in nameFields:
	# 		if field in disco_entry.keys():

	#Does the song exist?  If not, add it
import os

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tangodjango.settings")

#pugLetters = "A B C D E F G H I J L M N O P Q R S T U V W Y Z".split(' ')
pugLetters = ['A']
for letter in pugLetters:
	for song in parseTodoDisco(url + letter):
		lyricist = 'lyricist' in song.keys() if song['lyricist'] else {}
		addSong(song['title'], song['composer'], )
