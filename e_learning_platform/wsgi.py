"""
WSGI config for e_learning_platform project.
WSGI = Web Server Gateway Interface.
This is the entry point when deploying the app to a real web server.
Beginners: You don't need to change this file.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_learning_platform.settings')
application = get_wsgi_application()
