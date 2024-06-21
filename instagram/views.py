from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import shutil
import os

from .models import Comment, Post, PostImage, UserFollowing
from .serializers import CommentSerializer, PostSerializer, UserSerializer


class LoginView(APIView):
	def post(self, request):
		if User.objects.filter(username=request.data['username']).exists():
			user = User.objects.get(username=request.data['username'])
			if user.check_password(request.data['password']):
				token, created = Token.objects.get_or_create(user=user)
				user = Token.objects.get(key=token).user
				data = UserSerializer(user, context={'request': request, 'user_id': user.id}).data
				data['token'] = user.auth_token.key
				return Response(data, status=200)
			else:
				return Response({
					'msg': 'Incorrect password.',
				}, status=202)
		else:
			return Response({
				'msg': 'User with this name does not exist.',
			}, status=202)


class InitAuthView(APIView):
	def get(self, request):
		token = request.META.get('HTTP_AUTHORIZATION')
		if Token.objects.filter(key=token).exists():
			user = Token.objects.get(key=token).user
			data = UserSerializer(user, context={'request': request, 'user_id': user.id}).data
			data['token'] = user.auth_token.key
			return Response(data, status=200)
		else:
			return Response({'msg': 'There is no user with given token.'}, status=202)


class RegisterView(APIView):
	def post(self, request):

		if User.objects.filter(username=request.data['username']).exists():
			return Response({'msg': 'A user with the same name already exists.'}, status=202)
		else:
			user = User.objects.create(username=request.data['username'])
			user.set_password(request.data['password'])
			user.save()
			return Response({'msg': 'Account created. Please log in.'}, status=200)


class PostView(APIView):
	def get(self, request):
		"""
		Happens when the user comes to the site main page.
		If the user is authorized (there is a valid token in request headers),
		the method returns posts of him followed users.
		If the user is not authorized, the method returns all posts.
		ToDo: Return new portion of posts when the user scrolls to the bottom of the page.
		"""
		token = request.META.get('HTTP_AUTHORIZATION')  # For identification the user.
		# start_id lets know the id for the last fetched post from client.
		# The first post in this query is the post with id that is lower than start_id.
		# If start_id is "0", it means that there is no posts on client yet.
		# In this case, posts will be queried without "posts.filter(pk__lt=start_id)".
		start_id = int(self.request.query_params.get('startId'))
		# The user is authorized.
		if Token.objects.filter(key=token).exists():
			# Get the User instance, that the request was send from.
			user = Token.objects.get(key=token).user
			# Get the following instances, where "follower" is "user".
			followings = UserFollowing.objects.filter(follower=user)
			if len(followings) == 0:
				return Response({'msg': 'Follow users to see their posts.'}, status=202)
			# Initiate an array in which there will be users followed by "user".
			# Add here "user" himself so he will see it's own posts in feed.
			followed_users = [user]
			# Populate "followed_users" with followed users.
			for following in followings:
				followed_users.append(following.followed_user)
			# Get posts with owner who is in "followed_users" array.
			posts = Post.objects.filter(owner__in=followed_users).order_by('-pk')
			# Is the are posts in client already. Discards the posts that client fetched before.
			if start_id != 0:
				posts = posts.filter(pk__lt=start_id)
			# Defines portion of response.
			posts = posts[:5]
			# Indicates that "user" hasn't followed anybody and has never published his own posts.
			post_data = PostSerializer(posts, many=True, context={'request': request, 'user_id': user.id}).data
		# The the user is unauthorized, return all posts without filter by following.
		else:
			posts = Post.objects.all().order_by('-pk')
			if start_id != 0:
				posts = posts.filter(pk__lt=start_id)
			posts = posts[:5]
			post_data = PostSerializer(posts, many=True, context={'request': request, 'user_id': None}).data
		are_posts_over = False if len(posts) == 5 else True
		return Response({'posts': post_data, 'are_posts_over': are_posts_over}, status=200)

	def post(self, request):
		token = request.META.get('HTTP_AUTHORIZATION')
		if Token.objects.filter(key=token).exists():
			user = Token.objects.get(key=token).user
			post = Post.objects.create(caption=request.data['caption'], owner=user)
			images = dict((request.data).lists())['images']
			for image in images:
				PostImage.objects.create(image=image, post=post)
			data = PostSerializer(post, context={'request': request, 'user_id': user.id}).data
			return Response({'post': data}, status=200)
		else:
			return Response({'msg': 'You are not authorized.'}, status=202)

	def delete(self, request, pk):
		Post.objects.get(pk=pk).delete()
		return Response({'msg': 'Post has been deleted.'}, status=200)


class AvatarView(APIView):
	def post(self, request):
		token = request.META.get('HTTP_AUTHORIZATION')
		if Token.objects.filter(key=token).exists():
			user = Token.objects.get(key=token).user
			if os.path.isdir(f'media/avatars/{str(user.username)}'):
				shutil.rmtree(f'media/avatars/{str(user.username)}')
			user.profile.avatar = request.data['avatar']
			user.profile.save()
			avatar = request.build_absolute_uri(user.profile.avatar_url)
			return Response({'avatar': avatar}, status=200)
		else:
			return Response({'msg': 'You are not authorized.'}, status=202)

	def delete(self, request):
		token = request.META.get('HTTP_AUTHORIZATION')
		if Token.objects.filter(key=token).exists():
			user = Token.objects.get(key=token).user
			if os.path.isdir(f'media/avatars/{str(user.username)}'):
				shutil.rmtree(f'media/avatars/{str(user.username)}')
			user.profile.avatar = 'static/default_avatar.jpg'
			user.profile.save()
			avatar = request.build_absolute_uri(user.profile.avatar_url)
			return Response({'avatar': avatar}, status=200)
		else:
			return Response({'msg': 'You are not authorized.'}, status=202)


class UserView(APIView):
	def get(self, request):
		token = request.META.get('HTTP_AUTHORIZATION')
		users = User.objects.all().order_by('-pk')
		if Token.objects.filter(key=token).exists():
			user = Token.objects.get(key=token).user
			data = UserSerializer(users, many=True, context={'request': request, 'user_id': user.id}).data
			return Response(data, status=200)
		else:
			data = UserSerializer(users, many=True, context={'request': request, 'user_id': None}).data
			return Response(data, status=200)


class FollowView(APIView):
	def put(self, request, pk):
		token = request.META.get('HTTP_AUTHORIZATION')
		if Token.objects.filter(key=token).exists():
			user = Token.objects.get(key=token).user
			followed_user = User.objects.get(pk=pk)
			if UserFollowing.objects.filter(followed_user=followed_user, follower=user).exists():
				UserFollowing.objects.get(followed_user=followed_user, follower=user).delete()
			else:
				UserFollowing.objects.create(followed_user=followed_user, follower=user)
			return Response({'msg': 'Following created / removed.'}, status=200)
		else:
			return Response({'msg': 'You are not authorized.'}, status=202)


class LikeView(APIView):
	def put(self, request, pk):
		token = request.META.get('HTTP_AUTHORIZATION')
		if Token.objects.filter(key=token).exists():
			user = Token.objects.get(key=token).user
			post = Post.objects.get(pk=pk)
			if post.likes.filter(id=user.id).exists():
				post.likes.remove(user)
				return Response({'msg': 'Like removed.'}, status=200)
			else:
				post.likes.add(user)
				return Response({'msg': 'Like added.'}, status=200)
		else:
			return Response({'msg': 'You are not authorized.'}, status=202)


class CommentView(APIView):
	def post(self, request, pk):
		token = request.META.get('HTTP_AUTHORIZATION')
		if Token.objects.filter(key=token).exists():
			author = Token.objects.get(key=token).user
			body = request.data['body']
			post = Post.objects.get(id=pk)
			comment = Comment.objects.create(author=author, body=body, post=post)
			data = CommentSerializer(comment,  context={'request': request, 'user_id': author.id}).data
			return Response({'comment': data}, status=200)
		else:
			return Response({'msg': 'You are not authorized.'}, status=202)

	def delete(self, request, pk):
		token = request.META.get('HTTP_AUTHORIZATION')
		if Token.objects.filter(key=token).exists():
			Comment.objects.get(pk=pk).delete()
			return Response({'msg': 'Ok, comment deleted.'}, status=200)
		else:
			return Response({'msg': 'You are not authorized.'}, status=202)