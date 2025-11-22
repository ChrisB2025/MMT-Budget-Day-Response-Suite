"""Bingo URL configuration"""
from django.urls import path
from . import views

app_name = 'bingo'

urlpatterns = [
    path('', views.bingo_home, name='home'),
    path('generate/', views.generate_card, name='generate'),
    path('card/<int:card_id>/', views.card_detail, name='card_detail'),
    path('mark/<int:square_id>/', views.mark_square_view, name='mark_square'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('stats/', views.stats_view, name='stats'),
]
