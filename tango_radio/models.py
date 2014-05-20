from django.db import models
from unidecode import unidecode
from tango_disco.models import Recording
from django.contrib.auth.models import User
from django.conf import settings


class Tanda(models.Model):
	firstSong = models.ForeignKey(Recording, related_name='firstSong')
	secondSong = models.ForeignKey(Recording, null=True, blank=True, related_name='secondSong')
	thirdSong = models.ForeignKey(Recording, null=True, blank=True, related_name='thirdSong')
	fourthSong = models.ForeignKey(Recording, null=True, blank=True, related_name='fourthSong')
	createdby = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)