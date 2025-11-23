"""URL configuration for media complaints"""
from django.urls import path
from . import views

app_name = 'media_complaints'

urlpatterns = [
    # Home and main pages
    path('', views.complaints_home, name='home'),
    path('submit/', views.submit_complaint, name='submit'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('community/', views.community_complaints, name='community'),
    path('stats/', views.complaint_stats, name='stats'),

    # Individual complaint pages
    path('<int:complaint_id>/', views.view_complaint, name='view_complaint'),
    path('<int:complaint_id>/regenerate/', views.regenerate_letter, name='regenerate_letter'),
    path('<int:complaint_id>/send/', views.send_letter, name='send_letter'),
    path('<int:complaint_id>/delete/', views.delete_complaint, name='delete_complaint'),
    path('<int:complaint_id>/preview/', views.preview_letter, name='preview_letter'),

    # Outlet suggestions
    path('suggest-outlet/', views.suggest_outlet, name='suggest_outlet'),
    path('my-suggestions/', views.my_suggestions, name='my_suggestions'),
    path('suggestions/<int:suggestion_id>/', views.view_suggestion, name='view_suggestion'),
]
