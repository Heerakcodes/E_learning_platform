"""
apps.py — App Configuration for the 'courses' app.

Django uses this to register our app and its settings.
The name 'courses' must match the folder name and the entry in INSTALLED_APPS.
"""

from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'
    verbose_name = 'E-Learning Courses'  # Human-readable name shown in admin
