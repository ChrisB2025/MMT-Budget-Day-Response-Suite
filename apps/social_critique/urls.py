"""URL configuration for social critique app"""
from django.urls import path
from . import views

app_name = 'social_critique'

urlpatterns = [
    # Main pages
    path('', views.critique_home, name='home'),
    path('submit/', views.submit_critique, name='submit'),
    path('queue/', views.critique_queue, name='queue'),
    path('my-critiques/', views.my_critiques, name='my_critiques'),

    # Critique detail views
    path('c/<uuid:share_id>/', views.critique_detail, name='detail'),
    path('share/<uuid:share_id>/', views.public_critique_view, name='public_view'),

    # AJAX endpoints
    path('preview/', views.preview_url, name='preview_url'),
    path('c/<uuid:share_id>/upvote/', views.upvote_critique, name='upvote'),
    path('c/<uuid:share_id>/delete/', views.delete_critique, name='delete'),
    path('c/<uuid:share_id>/regenerate/', views.regenerate_replies, name='regenerate'),

    # Share link generation
    path('c/<uuid:share_id>/share/<str:platform>/', views.get_share_link, name='share_link'),
    path('c/<uuid:share_id>/copy/<str:reply_type>/<str:platform>/',
         views.copy_reply_content, name='copy_reply'),
]
