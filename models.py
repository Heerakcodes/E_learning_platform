"""
models.py — Database Models for the E-Learning Platform.

HOW DJANGO MODELS WORK:
- Each class here = one table in the MySQL database.
- Each attribute = one column in that table.
- Django automatically creates the SQL CREATE TABLE statements for us.
- ForeignKey creates a link (relationship) between two tables.

DATABASE TABLES CREATED:
  1. UserProfile  → Extends Django's built-in User to add a 'role' field
  2. Course       → Stores course information
  3. Module       → Individual lessons/chapters inside a course
  4. Enrollment   → Tracks which student enrolled in which course
  5. StudentProgress → Tracks which modules a student has completed
  6. Certificate  → Auto-issued when student reaches 100% completion
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ============================================================
# 1. USER PROFILE — Extends Django's built-in User model
#    Django already handles username, password, email, etc.
#    We add a 'role' field to distinguish Admins from Students.
# ============================================================
class UserProfile(models.Model):
    """
    Extends the built-in Django User model with a role.
    Each User has exactly one UserProfile (OneToOneField).
    """

    # Role choices — only two types of users
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]

    # OneToOneField means: one User ↔ one UserProfile (like a 1-to-1 relationship)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # If User is deleted, delete their Profile too
        related_name='profile'     # Access profile via: user.profile
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'          # New accounts are students by default
    )

    # Bio is optional (blank=True, null=True means it can be empty)
    bio = models.TextField(blank=True, null=True)

    # Profile picture (optional)
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    def __str__(self):
        """This controls how the object appears in admin and shell (e.g., "Alice (student)")"""
        return f"{self.user.username} ({self.role})"

    def is_admin(self):
        """Convenience method: returns True if this user is an admin"""
        return self.role == 'admin'

    def is_student(self):
        """Convenience method: returns True if this user is a student"""
        return self.role == 'student'

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


# ============================================================
# 2. COURSE — Represents a course (e.g., "Python Basics")
# ============================================================
class Course(models.Model):
    """
    A course is the main learning unit.
    Example: "Introduction to Python", "Web Development with Django"
    """

    title = models.CharField(max_length=200)          # Course name
    description = models.TextField()                  # Full course description
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        blank=True,
        null=True
    )

    # The admin who created this course
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # If admin is deleted, keep the course (set to NULL)
        null=True,
        blank=True,
        related_name='created_courses'
    )

    created_at = models.DateTimeField(default=timezone.now)  # Auto-timestamp
    is_published = models.BooleanField(default=True)         # Hide unpublished courses

    def __str__(self):
        return self.title

    def total_modules(self):
        """Returns how many modules this course has (used for progress calculation)"""
        return self.modules.count()  # 'modules' comes from Module's related_name

    def get_enrollment_count(self):
        """Returns how many students have enrolled in this course"""
        return self.enrollments.count()  # 'enrollments' from Enrollment's related_name

    class Meta:
        ordering = ['-created_at']  # Newest courses appear first
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


# ============================================================
# 3. MODULE — A single lesson/chapter inside a course
#    Example: Course "Python Basics" → Module 1 "Variables", Module 2 "Loops"
# ============================================================
class Module(models.Model):
    """
    A module is one lesson/chapter within a course.
    Students complete modules one by one to finish a course.
    """

    # ForeignKey: Many modules belong to one course
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,  # If course is deleted, delete all its modules
        related_name='modules'     # Access via: course.modules.all()
    )

    title = models.CharField(max_length=200)   # Module title
    content = models.TextField(blank=True)     # Lesson text/notes
    module_order = models.PositiveIntegerField(default=1)  # Order within the course (1, 2, 3...)
    duration_minutes = models.PositiveIntegerField(default=30)  # Estimated time to complete

    def __str__(self):
        return f"{self.course.title} — Module {self.module_order}: {self.title}"

    class Meta:
        ordering = ['module_order']  # Always show modules in order (1, 2, 3...)
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'


# ============================================================
# 4. ENROLLMENT — Records which student joined which course
# ============================================================
class Enrollment(models.Model):
    """
    Records a student's enrollment in a course.
    One student can enroll in many courses.
    One course can have many students enrolled.
    (This is a Many-to-Many relationship using a separate table)
    """

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'  # Access via: user.enrollments.all()
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'  # Access via: course.enrollments.all()
    )

    enrolled_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

    class Meta:
        # A student cannot enroll in the same course twice
        unique_together = ('student', 'course')
        ordering = ['-enrolled_date']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'


# ============================================================
# 5. STUDENT PROGRESS — Tracks module completion per student
# ============================================================
class StudentProgress(models.Model):
    """
    Tracks whether a specific student has completed a specific module.
    Also stores the score they got for that module (if applicable).

    This is the KEY table for calculating progress percentages.
    """

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )

    # True = student has completed this module, False = not yet
    is_completed = models.BooleanField(default=False)

    # Optional score for this module (0.00 to 100.00)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(null=True, blank=True)  # When they finished it

    def __str__(self):
        status = "✓ Completed" if self.is_completed else "○ In Progress"
        return f"{self.student.username} | {self.module.title} | {status}"

    class Meta:
        # A student cannot have duplicate records for the same module
        unique_together = ('student', 'module')
        verbose_name = 'Student Progress'
        verbose_name_plural = 'Student Progress Records'


# ============================================================
# 6. CERTIFICATE — Auto-issued when student completes 100% of a course
# ============================================================
class Certificate(models.Model):
    """
    Issued automatically when a student completes all modules in a course.
    The system checks completion % and marks is_eligible = True.
    """

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    issue_date = models.DateTimeField(default=timezone.now)

    # True = student finished the course and deserves the certificate
    is_eligible = models.BooleanField(default=False)

    # A unique certificate ID for display purposes
    certificate_id = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        eligible_str = "ELIGIBLE" if self.is_eligible else "Not eligible"
        return f"Certificate: {self.student.username} — {self.course.title} [{eligible_str}]"

    def save(self, *args, **kwargs):
        """Auto-generate a certificate ID when saving for the first time"""
        if not self.certificate_id:
            import uuid
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        # One certificate per student per course
        unique_together = ('student', 'course')
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
