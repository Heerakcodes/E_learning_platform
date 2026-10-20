"""
manage.py — Django's command-line utility for administrative tasks.

How to use:
    python manage.py runserver       → Start the development web server
    python manage.py makemigrations  → Create database migration files
    python manage.py migrate         → Apply migrations to the database
    python manage.py createsuperuser → Create an admin account
    python manage.py shell           → Open an interactive Python shell
"""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_learning_platform.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and available on "
            "your PYTHONPATH environment variable. Did you forget to activate a "
            "virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
