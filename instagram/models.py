import os
import uuid
import shutil
from django.db import models
from django.contrib.auth.models import User


def post_images_upload_path(instance, filename):
	return f'images/{str(instance.post.uuid)}/{filename}'


def avatar_upload_path(instance, filename):
	return f'avatars/{str(instance.user.username)}/{filename}'


class Post(models.Model):
	caption = models.CharField(max_length=2000)
	owner = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
	published_at = models.DateTimeField(auto_now_add=True)
	uuid = models.UUIDField(default=uuid.uuid4, editable=False)
	likes = models.ManyToManyField(User, related_name='post_like', default=0)

	def delete(self, *args, **kwargs):
		if os.path.isdir(f'media/images/{str(self.uuid)}'):
			shutil.rmtree(f'media/images/{str(self.uuid)}')
		super().delete(*args, **kwargs)  # Call the "real" delete() method.

	def total_likes(self):
		return self.likes.count()


class PostImage(models.Model):
	image = models.ImageField(upload_to=post_images_upload_path)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')


class Comment(models.Model):
	added_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
	body = models.CharField(max_length=2000)
	post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)


class Profile(models.Model):
	"""
	Extending the User model. Generally speaking, you will never have to call the Profile’s save method.
	Everything is done through the User model.
	"""
	avatar = models.ImageField(upload_to=avatar_upload_path, default='static/default_avatar.jpg')
	bio = models.TextField(max_length=500, blank=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

	@property
	def avatar_url(self):
		if self.avatar and hasattr(self.avatar, 'url'):
			return self.avatar.url
		else:
			return ''


class UserFollowing(models.Model):
	follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
	followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_users')