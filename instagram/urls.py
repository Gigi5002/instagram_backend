from django.urls import path
from . import views


urlpatterns = [
    path('avatar/', views.AvatarView.as_view()),
    path('comment/<int:pk>/', views.CommentView.as_view()),
    path('follow/<int:pk>/', views.FollowView.as_view()),
    path('init_auth/', views.InitAuthView.as_view()),
    path('like/<int:pk>/', views.LikeView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('posts/', views.PostView.as_view()),
    path('posts/<int:pk>/', views.PostView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('users/', views.UserView.as_view()),
]