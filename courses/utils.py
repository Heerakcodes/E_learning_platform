"""
utils.py — Helper Functions for the E-Learning Platform

This file contains reusable utility functions that are called from views.py.
Keeping these helper functions separate from views.py makes the code cleaner
and easier to understand — each function does ONE specific job.

FUNCTIONS IN THIS FILE:
  - calculate_progress()         → Computes completion % for a student in a course
  - check_and_award_certificate() → Issues a certificate when student reaches 100%
  - get_course_report_data()     → Gathers statistics for admin performance reports
  - get_student_dashboard_data() → Gathers all data for the student's dashboard
"""

from decimal import Decimal
from django.utils import timezone
from .models import (
    Course, Module, Enrollment, StudentProgress, Certificate, UserProfile
)


# ============================================================
# FUNCTION 1: Calculate a student's progress in a course
# ============================================================
def calculate_progress(student, course):
    """
    Calculates what percentage of a course a student has completed.

    FORMULA:
        Progress % = (Completed Modules / Total Modules) × 100

    Args:
        student  : A Django User object (the student)
        course   : A Course model object

    Returns:
        A dictionary with:
          - 'percentage'          : Float (0.0 to 100.0)
          - 'completed_count'     : How many modules are done
          - 'total_count'         : Total modules in the course
          - 'remaining_count'     : How many modules are left
          - 'is_complete'         : True if progress is 100%

    Example:
        If a course has 5 modules and student finished 3:
        percentage = (3 / 5) × 100 = 60.0%
    """

    # Step 1: Count total modules in the course
    total_modules = Module.objects.filter(course=course).count()

    # Edge case: If the course has NO modules yet, return 0%
    if total_modules == 0:
        return {
            'percentage': 0.0,
            'completed_count': 0,
            'total_count': 0,
            'remaining_count': 0,
            'is_complete': False,
        }

    # Step 2: Count how many modules THIS student has completed
    completed_modules = StudentProgress.objects.filter(
        student=student,
        module__course=course,  # Only modules that belong to this course
        is_completed=True       # Only completed ones
    ).count()

    # Step 3: Apply the formula
    percentage = (completed_modules / total_modules) * 100

    return {
        'percentage': round(percentage, 1),          # Round to 1 decimal place
        'completed_count': completed_modules,
        'total_count': total_modules,
        'remaining_count': total_modules - completed_modules,
        'is_complete': percentage >= 100.0,
    }


# ============================================================
# FUNCTION 2: Check eligibility and auto-issue a certificate
# ============================================================
def check_and_award_certificate(student, course):
    """
    Checks if a student has completed 100% of a course.
    If yes, automatically creates/updates their Certificate record.

    This is called every time a student marks a module as complete.

    Args:
        student : Django User object
        course  : Course model object

    Returns:
        The Certificate object if eligible, None otherwise.
    """

    # Calculate current progress
    progress = calculate_progress(student, course)

    if progress['is_complete']:
        # Student completed all modules! Issue or update the certificate.
        # get_or_create() returns (object, created_bool)
        certificate, created = Certificate.objects.get_or_create(
            student=student,
            course=course,
            defaults={
                'is_eligible': True,
                'issue_date': timezone.now()
            }
        )

        if not created and not certificate.is_eligible:
            # Certificate existed but wasn't marked eligible yet — fix that
            certificate.is_eligible = True
            certificate.issue_date = timezone.now()
            certificate.save()

        return certificate

    return None  # Not yet eligible


# ============================================================
# FUNCTION 3: Generate report data for the Admin Dashboard
# ============================================================
def get_course_report_data():
    """
    Generates performance statistics for EVERY course.
    Used in the admin report page to show an overview.

    Returns a list of dictionaries, one per course:
    [
        {
            'course': <Course object>,
            'total_enrolled': 15,
            'completed_students': 7,
            'completion_rate': 46.7,
            'avg_score': 78.5,
        },
        ...
    ]

    All numbers are computed from real database queries — no fake data!
    """

    from django.db.models import Avg, Count, Q

    report_data = []

    # Loop through every published course
    for course in Course.objects.filter(is_published=True):
        # How many students are enrolled?
        total_enrolled = Enrollment.objects.filter(course=course).count()

        # How many students completed ALL modules in this course?
        # A student is "complete" if they have a Certificate marked is_eligible=True
        completed_students = Certificate.objects.filter(
            course=course,
            is_eligible=True
        ).count()

        # Completion Rate = (Completed Students / Total Enrolled) × 100
        if total_enrolled > 0:
            completion_rate = round((completed_students / total_enrolled) * 100, 1)
        else:
            completion_rate = 0.0

        # Average score across all StudentProgress records for this course
        # We use Django's Avg() aggregation function
        avg_score_result = StudentProgress.objects.filter(
            module__course=course,
            is_completed=True,
            score__isnull=False  # Only include records that have a score
        ).aggregate(avg=Avg('score'))

        avg_score = avg_score_result['avg']
        if avg_score is not None:
            avg_score = round(float(avg_score), 1)
        else:
            avg_score = 0.0

        report_data.append({
            'course': course,
            'total_enrolled': total_enrolled,
            'completed_students': completed_students,
            'completion_rate': completion_rate,
            'avg_score': avg_score,
        })

    return report_data


# ============================================================
# FUNCTION 4: Gather all data for the Student's Dashboard
# ============================================================
def get_student_dashboard_data(student):
    """
    Returns all the information needed to render the student's dashboard.
    This includes enrolled courses, progress for each, and certificates.

    Args:
        student : Django User object

    Returns a dictionary:
    {
        'enrolled_courses': [
            {
                'enrollment': <Enrollment object>,
                'course': <Course object>,
                'progress': {percentage: 60.0, completed_count: 3, ...},
                'certificate': <Certificate object or None>,
            },
            ...
        ],
        'total_enrolled': 3,
        'total_completed': 1,
        'total_certificates': 1,
    }
    """

    enrolled_courses_data = []

    # Get all courses this student is enrolled in
    enrollments = Enrollment.objects.filter(student=student).select_related('course')

    for enrollment in enrollments:
        course = enrollment.course

        # Calculate progress for this specific course
        progress = calculate_progress(student, course)

        # Check if they have a certificate for this course
        try:
            certificate = Certificate.objects.get(
                student=student,
                course=course,
                is_eligible=True
            )
        except Certificate.DoesNotExist:
            certificate = None

        enrolled_courses_data.append({
            'enrollment': enrollment,
            'course': course,
            'progress': progress,
            'certificate': certificate,
        })

    # Summary stats — all computed from database, not hardcoded
    total_enrolled = len(enrolled_courses_data)
    total_completed = sum(
        1 for item in enrolled_courses_data if item['progress']['is_complete']
    )
    total_certificates = Certificate.objects.filter(
        student=student,
        is_eligible=True
    ).count()

    return {
        'enrolled_courses': enrolled_courses_data,
        'total_enrolled': total_enrolled,
        'total_completed': total_completed,
        'total_certificates': total_certificates,
    }
