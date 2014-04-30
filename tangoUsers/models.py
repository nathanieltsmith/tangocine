from django.contrib.auth.models import User
from django.db import models
from allauth.account.models import EmailAddress
from tango_perfs.models import Performers, Performances
from allauth.socialaccount.models import SocialAccount
import hashlib
# Create your models here.

class UserProfile(models.Model):
	favoritePerformers = models.ManyToManyField(Performer,related_name='favoritePerformers', null=True, blank=True)
	likedPerformances = models.ManyToManyField(Performance,related_name='likedPerformances', null=True, blank=True)
	viewdPerformances = models.ManyToManyField(Performance,related_name='viewedPerformances', null=True, blank=True)
	user = models.ForeignKey(User, unique=True)

	def __unicode__(self):
		return unicode(self.user)

	def account_verified(self):
		if self.user.is_authenticated:
			result = EmailAddress.objects.filter(email=self.user.email)
			if len(result):
				return result[0].verified
		return False

	def profile_image_url(self):
		fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')
 		if len(fb_uid):
			return "http://graph.facebook.com/{}/picture?width=40&height=40".format(fb_uid[0].uid)
		return "http://www.gravatar.com/avatar/{}?s=40".format(hashlib.md5(self.user.email).hexdigest())


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

class PerformerUserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	confirmed = models.BooleanField(default=False)
	showLikedVideos = models.BooleanField(default=True)
	english_bio = models.TextField(max_length=900, null=True, blank=True)
	spanish_bio = models.TextField(max_length=900, null=True, blank=True)
	facebook_link = models.URLField(max_length=100, null=True, blank=True)
	website_link = models.URLField(max_length=100, null=True, blank=True)
	twitter_link = models.URLField(max_length=100, null=True, blank=True)