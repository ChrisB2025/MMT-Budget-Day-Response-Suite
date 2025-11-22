"""Fact-check URL configuration"""
from django.urls import path
from . import views

app_name = 'factcheck'

urlpatterns = [
    path('', views.factcheck_home, name='home'),
    path('submit/', views.submit_factcheck, name='submit'),
    path('queue/', views.factcheck_queue, name='queue'),
    path('<int:request_id>/', views.factcheck_detail, name='detail'),
    path('<int:request_id>/upvote/', views.upvote_factcheck, name='upvote'),
    path('stats/', views.factcheck_stats, name='stats'),
]
