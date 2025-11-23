"""Fact-check URL configuration"""
from django.urls import path
from . import views

app_name = 'factcheck'

urlpatterns = [
    # Main pages
    path('', views.factcheck_home, name='home'),
    path('submit/', views.submit_factcheck, name='submit'),
    path('queue/', views.factcheck_queue, name='queue'),
    path('<int:request_id>/', views.factcheck_detail, name='detail'),
    path('stats/', views.factcheck_stats, name='stats'),

    # Competition features
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('live-feed/', views.live_feed_view, name='live_feed'),

    # User features
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('profile/<int:user_id>/follow/', views.follow_user, name='follow_user'),

    # Social features
    path('<int:request_id>/upvote/', views.upvote_factcheck, name='upvote'),
    path('<int:request_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:request_id>/share/', views.share_to_twitter, name='share_twitter'),
]
