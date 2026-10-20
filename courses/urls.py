"""
urls.py — URL Routing for the 'courses' App

This file maps URL patterns to view functions.
Think of it as a "table of contents" that matches web addresses to pages.

FORMAT: path('url-pattern/', view_function, name='url-name')
  - The 'name' is used in templates as {% url 'name' %} to generate links.
    This means if you change the URL pattern, all links update automatically!

URL STRUCTURE:
  /                       → Home/landing page
  /register/              → Create new account
  /login/                 → Log in
  /logout/                → Log out
  /dashboard/             → Student dashboard
  /courses/               → Browse all courses
  /courses/<id>/          → Course detail & modules
  /courses/<id>/enroll/   → Enroll in a course
  /module/<id>/complete/  → Mark module as complete
  /certificate/<id>/      → View certificate
  /admin-panel/           → Admin dashboard
  /admin-panel/courses/   → Manage courses (CRUD)
  /admin-panel/reports/   → Performance reports
  /admin-panel/students/  → Student records
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── AUTHENTICATION ──────────────────────────────────────────
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── STUDENT VIEWS ────────────────────────────────────────────
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('module/<int:module_id>/complete/', views.mark_module_complete, name='mark_module_complete'),
    path('certificate/<int:course_id>/', views.view_certificate, name='view_certificate'),

    # ── ADMIN VIEWS ──────────────────────────────────────────────
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/courses/', views.manage_courses, name='manage_courses'),
    path('admin-panel/courses/add/', views.add_course, name='add_course'),
    path('admin-panel/courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('admin-panel/courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('admin-panel/courses/<int:course_id>/add-module/', views.add_module, name='add_module'),
    path('admin-panel/modules/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('admin-panel/modules/<int:module_id>/delete/', views.delete_module, name='delete_module'),
    path('admin-panel/students/', views.student_records, name='student_records'),
    path('admin-panel/students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('admin-panel/reports/', views.report_view, name='report_view'),
]
