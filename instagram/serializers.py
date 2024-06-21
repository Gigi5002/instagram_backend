from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Comment, Post, PostImage


class UserSerializer(serializers.ModelSerializer):
    is_followed = serializers.SerializerMethodField('get_is_followed')

    class Meta:
        model = User

    def get_is_followed(self, instance):
        cur_user_id = self.context['user_id']
        if cur_user_id is not None:
            cur_user = User.objects.get(pk=cur_user_id)
            if cur_user.followers.filter(followed_user=instance).exists():
                return True
            else:
                return False
        else:
            return False

    def to_representation(self, instance):
        return {
            'avatar': self.context['request'].build_absolute_uri(instance.profile.avatar_url),
            'id': instance.id,
            'is_followed': self.get_is_followed(instance),
            'username': instance.username,
        }


class CommentSerializer(serializers.ModelSerializer):
    """ For PostSerializer. """
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('author', 'body', 'id')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image']

    def to_representation(self, instance):
        return self.context['request'].build_absolute_uri(instance.image.url)


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField('get_is_liked')
    owner = UserSerializer(read_only=True)

    def get_is_liked(self, instance):
        if instance.likes.filter(id=self.context['user_id']).exists():
            return True
        else:
            return False

    class Meta:
        model = Post
        fields = ('caption', 'comments', 'id', 'images', 'is_liked', 'owner', 'total_likes')
