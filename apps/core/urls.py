"""Core URL configuration"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('help/', views.help_page, name='help'),

    # Admin tools
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-test-submissions/', views.delete_test_submissions, name='delete_test_submissions'),
    path('reset-test-data/', views.reset_test_data, name='reset_test_data'),

    # EMERGENCY: No-login staff grant endpoint - TODO: REMOVE IMMEDIATELY AFTER USE!
    path('emergency-grant-staff/', views.grant_staff_emergency, name='grant_staff_emergency'),
]
