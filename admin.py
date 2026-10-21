"""
admin.py — Django Admin Panel Configuration

This registers our models with Django's built-in admin interface.
After running the server, go to http://127.0.0.1:8000/admin/ to access it.
You need a superuser account: python manage.py createsuperuser

We customize the admin display to show useful columns in the list view.
"""

from django.contrib import admin
from .models import UserProfile, Course, Module, Enrollment, StudentProgress, Certificate


# ── UserProfile Admin ─────────────────────────────────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'user__email')          # Columns to show in list
    list_filter = ('role',)                                  # Filter sidebar
    search_fields = ('user__username', 'user__email')        # Searchable fields


# ── Course Admin ─────────────────────────────────────────────────────────────
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'is_published', 'created_at', 'total_modules')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_published',)                        # Can toggle published right in the list!
    readonly_fields = ('created_at',)

    def total_modules(self, obj):
        """Shows module count in admin list"""
        return obj.total_modules()
    total_modules.short_description = 'Modules'


# ── Module Admin ─────────────────────────────────────────────────────────────
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'module_order', 'duration_minutes')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'module_order')


# ── Enrollment Admin ─────────────────────────────────────────────────────────
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_date')
    list_filter = ('course', 'enrolled_date')
    search_fields = ('student__username', 'course__title')
    readonly_fields = ('enrolled_date',)


# ── StudentProgress Admin ────────────────────────────────────────────────────
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'is_completed', 'score', 'completed_at')
    list_filter = ('is_completed', 'module__course')
    search_fields = ('student__username', 'module__title')
    list_editable = ('is_completed', 'score')


# ── Certificate Admin ────────────────────────────────────────────────────────
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'is_eligible', 'certificate_id', 'issue_date')
    list_filter = ('is_eligible', 'course')
    search_fields = ('student__username', 'course__title', 'certificate_id')
    readonly_fields = ('certificate_id', 'issue_date')
