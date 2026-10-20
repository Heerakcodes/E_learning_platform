"""
views.py — Application Logic for the E-Learning Platform

HOW VIEWS WORK:
- Each function here handles one URL/page.
- It receives an HTTP request, processes it (reads/writes DB), and returns an HTML response.
- We use Django's template system to combine Python data with HTML files.

VIEW FUNCTIONS IN THIS FILE:
  Authentication:
    - home()              → Welcome/landing page
    - register()          → Create new account
    - login_view()        → Log in
    - logout_view()       → Log out

  Student Views:
    - student_dashboard() → Student's personal dashboard
    - course_list()       → Browse all available courses
    - course_detail()     → View course modules & mark complete
    - enroll_course()     → Enroll in a course
    - mark_module_complete() → Mark a module as done
    - view_certificate()  → View/download certificate

  Admin Views:
    - admin_dashboard()   → Admin overview panel
    - manage_courses()    → List all courses (admin)
    - add_course()        → Create a new course
    - edit_course()       → Update an existing course
    - delete_course()     → Remove a course
    - add_module()        → Add a module to a course
    - edit_module()       → Update a module
    - delete_module()     → Remove a module
    - student_records()   → View all student enrollments
    - report_view()       → Performance report page
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count

from .models import Course, Module, Enrollment, StudentProgress, Certificate, UserProfile
from .utils import calculate_progress, check_and_award_certificate, get_course_report_data, get_student_dashboard_data


# ============================================================
# HELPER: Role-based access control decorators
# These are used to protect views from unauthorized access.
# ============================================================

def admin_required(view_func):
    """
    Custom decorator: Only allows admin users to access the view.
    If a non-admin tries to access it, they get redirected with an error message.

    Usage: @admin_required (placed above a view function)
    """
    def wrapper(request, *args, **kwargs):
        # First check if user is logged in
        if not request.user.is_authenticated:
            return redirect('login')

        # Then check if they have an admin profile
        try:
            if request.user.profile.role != 'admin':
                messages.error(request, "You don't have permission to access this page.")
                return redirect('student_dashboard')
        except UserProfile.DoesNotExist:
            messages.error(request, "Profile not found. Please contact support.")
            return redirect('login')

        return view_func(request, *args, **kwargs)

    wrapper.__name__ = view_func.__name__
    return wrapper


def student_required(view_func):
    """
    Custom decorator: Redirects admin users away from student-only pages.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if request.user.profile.role == 'admin':
                return redirect('admin_dashboard')
        except UserProfile.DoesNotExist:
            pass
        return view_func(request, *args, **kwargs)

    wrapper.__name__ = view_func.__name__
    return wrapper


# ============================================================
# SECTION 1: AUTHENTICATION VIEWS
# ============================================================

def home(request):
    """
    Landing page — shows a welcome screen with platform overview.
    Redirects logged-in users to their respective dashboards.
    """
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        except UserProfile.DoesNotExist:
            pass

    # Count real stats from database for the home page
    total_courses = Course.objects.filter(is_published=True).count()
    total_students = UserProfile.objects.filter(role='student').count()
    total_certificates = Certificate.objects.filter(is_eligible=True).count()

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_certificates': total_certificates,
    }
    return render(request, 'home.html', context)


def register(request):
    """
    Handles user registration.
    GET  → Show the registration form
    POST → Process the form data and create a new User + UserProfile
    """
    # If user is already logged in, no need to register again
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        # Extract form data
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', 'student')

        # Validation checks
        if not username or not email or not password1:
            messages.error(request, "Username, email, and password are required.")
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'register.html')

        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken. Choose another.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"An account with email '{email}' already exists.")
            return render(request, 'register.html')

        # Create the User object (Django handles password hashing automatically)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        # Create the UserProfile to store the role
        UserProfile.objects.create(user=user, role=role)

        # Log the user in immediately after registration
        login(request, user)
        messages.success(request, f"Welcome to EduLearn, {first_name or username}! Your account is ready.")

        # Redirect to appropriate dashboard based on role
        if role == 'admin':
            return redirect('admin_dashboard')
        return redirect('student_dashboard')

    # GET request: just show the empty registration form
    return render(request, 'register.html')


def login_view(request):
    """
    Handles user login.
    GET  → Show the login form
    POST → Verify credentials and log in
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'login.html')

        # Django's authenticate() checks username + password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")

            # Redirect based on role
            try:
                if user.profile.role == 'admin':
                    return redirect('admin_dashboard')
            except UserProfile.DoesNotExist:
                pass

            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'login.html')


def logout_view(request):
    """Logs the user out and redirects to the login page."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('login')
    return redirect('home')


# ============================================================
# SECTION 2: STUDENT VIEWS
# ============================================================

@login_required
@student_required
def student_dashboard(request):
    """
    The student's personal dashboard.
    Shows: enrolled courses, progress %, certificate status, summary stats.

    All numbers are computed dynamically using our utility function.
    """
    dashboard_data = get_student_dashboard_data(request.user)
    context = {
        'dashboard': dashboard_data,
        'page_title': 'My Dashboard',
    }
    return render(request, 'student_dashboard.html', context)


@login_required
def course_list(request):
    """
    Shows all published courses available on the platform.
    Students see an 'Enroll' button; admins see a 'Manage' button.
    """
    courses = Course.objects.filter(is_published=True)

    # Find which courses the current user is already enrolled in
    if request.user.is_authenticated:
        enrolled_course_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list('course_id', flat=True)
    else:
        enrolled_course_ids = []

    # Add module count to each course for display
    courses_with_info = []
    for course in courses:
        courses_with_info.append({
            'course': course,
            'module_count': course.total_modules(),
            'enrollment_count': course.get_enrollment_count(),
            'is_enrolled': course.id in enrolled_course_ids,
        })

    context = {
        'courses_with_info': courses_with_info,
        'page_title': 'Available Courses',
    }
    return render(request, 'course_list.html', context)


@login_required
def course_detail(request, course_id):
    """
    Shows the details of a specific course:
    - Course description
    - List of all modules
    - Which modules the student has completed (with checkmarks)
    - Overall progress % (computed dynamically)
    """
    course = get_object_or_404(Course, id=course_id, is_published=True)
    modules = Module.objects.filter(course=course).order_by('module_order')

    # Check if this student is enrolled
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course
    ).exists()

    # Get the student's progress for each module
    module_progress = {}
    if is_enrolled:
        progress_records = StudentProgress.objects.filter(
            student=request.user,
            module__course=course
        )
        # Create a dict: {module_id: progress_record}
        for record in progress_records:
            module_progress[record.module_id] = record

    # Build a list of modules with their completion status
    modules_with_status = []
    for module in modules:
        progress_record = module_progress.get(module.id)
        modules_with_status.append({
            'module': module,
            'is_completed': progress_record.is_completed if progress_record else False,
            'score': progress_record.score if progress_record else None,
            'completed_at': progress_record.completed_at if progress_record else None,
        })

    # Calculate overall course progress for this student
    progress = calculate_progress(request.user, course) if is_enrolled else None

    # Check certificate status
    certificate = None
    if is_enrolled:
        try:
            certificate = Certificate.objects.get(
                student=request.user,
                course=course,
                is_eligible=True
            )
        except Certificate.DoesNotExist:
            pass

    context = {
        'course': course,
        'modules_with_status': modules_with_status,
        'is_enrolled': is_enrolled,
        'progress': progress,
        'certificate': certificate,
        'page_title': course.title,
    }
    return render(request, 'course_detail.html', context)


@login_required
@student_required
def enroll_course(request, course_id):
    """
    Enrolls the current student in a course.
    Only accepts POST requests (form submission) for security.
    """
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id, is_published=True)

        # Check if already enrolled (prevent duplicate enrollments)
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.info(request, f"You are already enrolled in '{course.title}'.")
        else:
            Enrollment.objects.create(student=request.user, course=course)
            messages.success(request, f"Successfully enrolled in '{course.title}'! Start learning now.")

        return redirect('course_detail', course_id=course_id)

    return redirect('course_list')


@login_required
@student_required
def mark_module_complete(request, module_id):
    """
    Marks a specific module as completed for the current student.
    Also records a score (if provided) and checks for certificate eligibility.

    POST data:
        score (optional): A number between 0 and 100
    """
    if request.method == 'POST':
        module = get_object_or_404(Module, id=module_id)
        course = module.course

        # Make sure student is enrolled in this course
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.error(request, "You must enroll in the course before completing modules.")
            return redirect('course_detail', course_id=course.id)

        # Get optional score from form
        score_input = request.POST.get('score', '').strip()
        score = None
        if score_input:
            try:
                score = float(score_input)
                # Clamp score between 0 and 100
                score = max(0.0, min(100.0, score))
            except ValueError:
                score = None

        # get_or_create() avoids creating duplicate records
        progress_record, created = StudentProgress.objects.get_or_create(
            student=request.user,
            module=module,
            defaults={
                'is_completed': True,
                'score': score,
                'completed_at': timezone.now()
            }
        )

        if not created:
            # Record already exists — update it
            progress_record.is_completed = True
            if score is not None:
                progress_record.score = score
            progress_record.completed_at = timezone.now()
            progress_record.save()

        messages.success(request, f"'{module.title}' marked as complete!")

        # Automatically check if student is now eligible for a certificate
        certificate = check_and_award_certificate(request.user, course)
        if certificate:
            messages.success(
                request,
                f"🎉 Congratulations! You've completed all modules in '{course.title}'. "
                f"Your certificate is ready!"
            )

        return redirect('course_detail', course_id=course.id)

    return redirect('course_list')


@login_required
def view_certificate(request, course_id):
    """
    Displays a student's certificate for a completed course.
    Only accessible to the student who earned it (or admins).
    """
    course = get_object_or_404(Course, id=course_id)

    # Admins can view any certificate; students can only view their own
    if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
        student_id = request.GET.get('student_id')
        if student_id:
            student = get_object_or_404(User, id=student_id)
        else:
            student = request.user
    else:
        student = request.user

    certificate = get_object_or_404(
        Certificate,
        student=student,
        course=course,
        is_eligible=True
    )

    progress = calculate_progress(student, course)

    context = {
        'certificate': certificate,
        'course': course,
        'student': student,
        'progress': progress,
        'page_title': f'Certificate — {course.title}',
    }
    return render(request, 'certificate.html', context)


# ============================================================
# SECTION 3: ADMIN VIEWS
# ============================================================

@login_required
@admin_required
def admin_dashboard(request):
    """
    Admin's main dashboard showing:
    - Total courses, students, enrollments, certificates
    - Recent enrollments
    All numbers come from real database queries.
    """
    # Summary statistics (all from DB queries)
    total_courses = Course.objects.filter(is_published=True).count()
    total_students = UserProfile.objects.filter(role='student').count()
    total_enrollments = Enrollment.objects.count()
    total_certificates = Certificate.objects.filter(is_eligible=True).count()

    # 5 most recent enrollments for the "Recent Activity" section
    recent_enrollments = Enrollment.objects.select_related(
        'student', 'course'
    ).order_by('-enrolled_date')[:5]

    # Courses sorted by enrollment count (most popular first)
    popular_courses = []
    for course in Course.objects.filter(is_published=True):
        popular_courses.append({
            'course': course,
            'enrollment_count': course.get_enrollment_count(),
            'module_count': course.total_modules(),
        })
    popular_courses.sort(key=lambda x: x['enrollment_count'], reverse=True)
    popular_courses = popular_courses[:5]  # Top 5

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'total_certificates': total_certificates,
        'recent_enrollments': recent_enrollments,
        'popular_courses': popular_courses,
        'page_title': 'Admin Dashboard',
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
@admin_required
def manage_courses(request):
    """Lists all courses for the admin to manage (edit/delete)."""
    courses = Course.objects.all()
    courses_with_info = []
    for course in courses:
        courses_with_info.append({
            'course': course,
            'module_count': course.total_modules(),
            'enrollment_count': course.get_enrollment_count(),
        })

    context = {
        'courses_with_info': courses_with_info,
        'page_title': 'Manage Courses',
    }
    return render(request, 'manage_courses.html', context)


@login_required
@admin_required
def add_course(request):
    """
    Allows admin to create a new course.
    GET  → Show empty course creation form
    POST → Save new course to database
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        is_published = request.POST.get('is_published') == 'on'
        thumbnail = request.FILES.get('thumbnail')

        if not title or not description:
            messages.error(request, "Course title and description are required.")
            return render(request, 'course_form.html', {'action': 'Add', 'page_title': 'Add Course'})

        course = Course.objects.create(
            title=title,
            description=description,
            is_published=is_published,
            created_by=request.user,
            thumbnail=thumbnail
        )
        messages.success(request, f"Course '{course.title}' created successfully!")
        return redirect('manage_courses')

    return render(request, 'course_form.html', {'action': 'Add', 'page_title': 'Add Course'})


@login_required
@admin_required
def edit_course(request, course_id):
    """
    Allows admin to edit an existing course.
    GET  → Pre-fill the form with current course data
    POST → Save the updated data to the database
    """
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        is_published = request.POST.get('is_published') == 'on'

        if not title or not description:
            messages.error(request, "Course title and description are required.")
            return render(request, 'course_form.html', {
                'course': course, 'action': 'Edit', 'page_title': f'Edit: {course.title}'
            })

        course.title = title
        course.description = description
        course.is_published = is_published
        if request.FILES.get('thumbnail'):
            course.thumbnail = request.FILES['thumbnail']
        course.save()

        messages.success(request, f"Course '{course.title}' updated successfully!")
        return redirect('manage_courses')

    return render(request, 'course_form.html', {
        'course': course, 'action': 'Edit', 'page_title': f'Edit: {course.title}'
    })


@login_required
@admin_required
def delete_course(request, course_id):
    """
    Deletes a course (and all its modules/enrollments via CASCADE).
    Only accepts POST for safety (GET requests don't delete anything).
    """
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f"Course '{course_title}' and all its data have been deleted.")
        return redirect('manage_courses')

    # Show confirmation page
    context = {
        'course': course,
        'page_title': f'Delete: {course.title}',
    }
    return render(request, 'confirm_delete.html', context)


@login_required
@admin_required
def add_module(request, course_id):
    """
    Adds a new module to an existing course.
    GET  → Show module creation form
    POST → Save new module to database
    """
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        module_order = request.POST.get('module_order', 1)
        duration_minutes = request.POST.get('duration_minutes', 30)

        if not title:
            messages.error(request, "Module title is required.")
            return render(request, 'module_form.html', {
                'course': course, 'action': 'Add', 'page_title': 'Add Module'
            })

        try:
            module_order = int(module_order)
            duration_minutes = int(duration_minutes)
        except ValueError:
            module_order = 1
            duration_minutes = 30

        Module.objects.create(
            course=course,
            title=title,
            content=content,
            module_order=module_order,
            duration_minutes=duration_minutes
        )
        messages.success(request, f"Module '{title}' added to '{course.title}'!")
        return redirect('edit_course', course_id=course.id)

    # Auto-suggest next module order number
    next_order = Module.objects.filter(course=course).count() + 1

    return render(request, 'module_form.html', {
        'course': course,
        'action': 'Add',
        'next_order': next_order,
        'page_title': f'Add Module to {course.title}',
    })


@login_required
@admin_required
def edit_module(request, module_id):
    """Edit an existing module."""
    module = get_object_or_404(Module, id=module_id)
    course = module.course

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        module_order = request.POST.get('module_order', module.module_order)
        duration_minutes = request.POST.get('duration_minutes', module.duration_minutes)

        if not title:
            messages.error(request, "Module title is required.")
        else:
            try:
                module_order = int(module_order)
                duration_minutes = int(duration_minutes)
            except ValueError:
                module_order = module.module_order
                duration_minutes = module.duration_minutes

            module.title = title
            module.content = content
            module.module_order = module_order
            module.duration_minutes = duration_minutes
            module.save()
            messages.success(request, f"Module '{title}' updated successfully!")
            return redirect('edit_course', course_id=course.id)

    return render(request, 'module_form.html', {
        'module': module,
        'course': course,
        'action': 'Edit',
        'page_title': f'Edit Module: {module.title}',
    })


@login_required
@admin_required
def delete_module(request, module_id):
    """Delete a module from a course."""
    module = get_object_or_404(Module, id=module_id)
    course = module.course

    if request.method == 'POST':
        module_title = module.title
        module.delete()
        messages.success(request, f"Module '{module_title}' deleted successfully.")
        return redirect('edit_course', course_id=course.id)

    return render(request, 'confirm_delete.html', {
        'module': module,
        'course': course,
        'page_title': f'Delete Module: {module.title}',
    })


@login_required
@admin_required
def student_records(request):
    """
    Shows admin a list of all students and their enrollment/progress overview.
    """
    students = UserProfile.objects.filter(role='student').select_related('user')

    students_data = []
    for profile in students:
        user = profile.user
        enrollment_count = Enrollment.objects.filter(student=user).count()
        certificate_count = Certificate.objects.filter(student=user, is_eligible=True).count()

        students_data.append({
            'user': user,
            'profile': profile,
            'enrollment_count': enrollment_count,
            'certificate_count': certificate_count,
            'date_joined': user.date_joined,
        })

    context = {
        'students_data': students_data,
        'total_students': len(students_data),
        'page_title': 'Student Records',
    }
    return render(request, 'student_records.html', context)


@login_required
@admin_required
def student_detail(request, student_id):
    """Shows detailed progress of a specific student across all their courses."""
    student = get_object_or_404(User, id=student_id)
    dashboard_data = get_student_dashboard_data(student)

    context = {
        'student': student,
        'dashboard': dashboard_data,
        'page_title': f'Progress: {student.get_full_name() or student.username}',
    }
    return render(request, 'student_detail.html', context)


@login_required
@admin_required
def report_view(request):
    """
    Performance report page for admins.
    Shows course-wise statistics: completion rates, average scores, enrollment counts.
    All data pulled directly from the database — no hardcoded numbers.
    """
    report_data = get_course_report_data()

    # Overall platform statistics
    total_students = UserProfile.objects.filter(role='student').count()
    total_enrollments = Enrollment.objects.count()
    total_completions = Certificate.objects.filter(is_eligible=True).count()

    if total_enrollments > 0:
        overall_completion_rate = round((total_completions / total_enrollments) * 100, 1)
    else:
        overall_completion_rate = 0.0

    context = {
        'report_data': report_data,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'total_completions': total_completions,
        'overall_completion_rate': overall_completion_rate,
        'page_title': 'Performance Reports',
    }
    return render(request, 'report.html', context)
