"""Core URL configuration"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('campaigns/', views.campaigns, name='campaigns'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('help/', views.help_page, name='help'),
    path('fun/', views.fun_page, name='fun'),
    path('league-table/', views.league_table, name='league_table'),
    path('health/', views.health_check, name='health_check'),

    # Admin tools
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-test-submissions/', views.delete_test_submissions, name='delete_test_submissions'),
    path('reset-test-data/', views.reset_test_data, name='reset_test_data'),
    path('grant-superuser/', views.grant_superuser_access, name='grant_superuser'),
]
