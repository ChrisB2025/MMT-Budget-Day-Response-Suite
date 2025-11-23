"""
URL configuration for budget_response_suite project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Django-allauth URLs (must be before users/)
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('bingo/', include('apps.bingo.urls')),
    path('factcheck/', include('apps.factcheck.urls')),
    path('rebuttal/', include('apps.rebuttal.urls')),
    path('complaints/', include('apps.media_complaints.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
