"""
Main URL Configuration for the E-Learning Platform project.

This file routes incoming web requests to the correct app.
Think of it as a "traffic controller" that reads the URL and decides
which app/view should handle the request.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django's built-in admin panel (only for superusers)
    path('admin/', admin.site.urls),

    # All our app URLs are defined in courses/urls.py
    # The '' means these routes start at the root URL (/)
    path('', include('courses.urls')),
]

# During development, serve uploaded media files (e.g., certificates)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
