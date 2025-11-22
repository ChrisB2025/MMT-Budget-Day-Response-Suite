"""Rebuttal URL configuration"""
from django.urls import path
from . import views

app_name = 'rebuttal'

urlpatterns = [
    path('', views.rebuttal_home, name='home'),
    path('latest/', views.latest_rebuttal, name='latest'),
    path('list/', views.rebuttal_list, name='list'),
    path('create/', views.create_rebuttal, name='create'),
    path('<int:rebuttal_id>/', views.rebuttal_detail, name='detail'),
    path('<int:rebuttal_id>/download/<str:format>/', views.download_rebuttal, name='download'),
]
