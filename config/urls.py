"""
URL configuration for budget_response_suite project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Convenience redirect for make-me-admin
    path('make-me-admin/', RedirectView.as_view(url='/users/make-me-admin/', permanent=False)),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('bingo/', include('apps.bingo.urls')),
    path('factcheck/', include('apps.factcheck.urls')),
    path('rebuttal/', include('apps.rebuttal.urls')),
    path('complaints/', include('apps.media_complaints.urls')),
    path('critique/', include('apps.social_critique.urls')),
    path('articles/', include('apps.article_critique.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
