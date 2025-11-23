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
    path('admin/delete-test-submissions/', views.delete_test_submissions, name='delete_test_submissions'),

    # TEMPORARY: One-time staff grant endpoint - TODO: Remove after use
    path('grant-staff-temp-chrisb/', views.grant_staff_temporary, name='grant_staff_temporary'),
]
