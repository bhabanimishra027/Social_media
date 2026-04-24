from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('feed/', views.feed, name='feed'),
    path('create/', views.create_post, name='create_post'),
    path('account/', views.account, name='account'),
    path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('follow/<int:user_id>/', views.follow_toggle, name='follow_toggle'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('like/<int:post_id>/', views.like_toggle, name='like_toggle'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<int:user_id>/', views.chat, name='chat'),
    path('share/<int:post_id>/', views.share_post, name='share_post'),
    path('reels/', views.reels, name='reels'),
    path('story/create/', views.create_story, name='create_story'),
    path('reel/create/', views.create_reel, name='create_reel'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('story/<int:story_id>/', views.view_story, name='view_story'),
    path('story/toggle/<int:story_id>/', views.toggle_story_highlight, name='toggle_story_highlight'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
]