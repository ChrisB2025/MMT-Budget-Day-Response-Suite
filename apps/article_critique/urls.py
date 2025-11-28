"""URL configuration for article critique app."""
from django.urls import path
from . import views

app_name = 'article_critique'

urlpatterns = [
    # Main pages
    path('', views.article_home, name='home'),
    path('submit/', views.submit_article_url, name='submit'),
    path('submit/text/', views.submit_article_text, name='submit_text'),
    path('queue/', views.article_queue, name='queue'),
    path('my-articles/', views.my_articles, name='my_articles'),

    # Article detail views
    path('a/<uuid:share_id>/', views.article_detail, name='detail'),
    path('share/<uuid:share_id>/', views.public_article_view, name='public_view'),

    # AJAX endpoints
    path('preview/', views.preview_article_url, name='preview_url'),
    path('a/<uuid:share_id>/upvote/', views.upvote_article, name='upvote'),
    path('a/<uuid:share_id>/delete/', views.delete_article, name='delete'),
    path('a/<uuid:share_id>/regenerate/', views.regenerate_responses, name='regenerate'),

    # Share link generation
    path('a/<uuid:share_id>/share/<str:platform>/', views.get_share_link, name='share_link'),
    path('a/<uuid:share_id>/copy/<str:response_type>/', views.copy_response_content, name='copy_response'),
]
