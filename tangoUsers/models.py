from django.db import models
from tango_perfs.models import Performers, Performances
# Create your models here.

class UserProfile(models.Model):
	favoritePerformers = models.ManyToManyField(Performer,related_name='favoritePerformers', null=True, blank=True)
	likedPerformances = models.ManyToManyField(Performance,related_name='likedPerformances', null=True, blank=True)
	viewdPerformances = models.ManyToManyField(Performance,related_name='viewedPerformances', null=True, blank=True)
	user = models.ForeignKey(User, unique=True)

	def __unicode__(self):
		return unicode(self.user)

class PerformerUserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	confirmed = models.BooleanField(default=False)
	showLikedVideos = models.BooleanField(default=True)
	english_bio = models.TextField(max_length=900, null=True, blank=True)
	spanish_bio = models.TextField(max_length=900, null=True, blank=True)
	facebook_link = models.URLField(max_length=100, null=True, blank=True)
	website_link = models.URLField(max_length=100, null=True, blank=True)
	twitter_link = models.URLField(max_length=100, null=True, blank=True)