"""
seed_data.py -- Database Seed Script for EduLearn Platform

PURPOSE:
    Populates the database with realistic sample data so the platform
    works right out of the box without manually entering data through the UI.

HOW TO RUN (from inside e_learning_platform/ folder):
    python seed_data.py

NOTE:
    Running this script twice is safe -- it skips already-existing records
    because we use get_or_create() throughout.

WHAT THIS CREATES:
    - 1 Admin user    : username=admin    / password=admin123
    - 4 Student users : username=alice/bob/charlie/diana / password=student123
    - 4 Courses with realistic module structures
    - Enrollments across students and courses
    - Student Progress (some complete, some partial -- realistic progress %)
    - Certificates auto-issued for students who completed all modules
"""

import os
import sys
import django

# -- SETUP DJANGO ENVIRONMENT ------------------------------------------
# This lets us run the script directly with: python seed_data.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_learning_platform.settings')

# Add the project directory to Python's path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

# -- NOW WE CAN IMPORT DJANGO MODELS -----------------------------------
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import UserProfile, Course, Module, Enrollment, StudentProgress, Certificate
from courses.utils import calculate_progress, check_and_award_certificate


print("=" * 60)
print("  EduLearn Seed Data Script")
print("  Creating sample data for the E-Learning Platform...")
print("=" * 60)


# ============================================================
# STEP 1: CREATE USERS
# ============================================================
print("\n[1/5] Creating users...")

# -- Admin user
admin_user, created = User.objects.get_or_create(username='admin')
if created:
    admin_user.set_password('admin123')
    admin_user.first_name = 'Admin'
    admin_user.last_name = 'User'
    admin_user.email = 'admin@edulearn.com'
    admin_user.save()
    UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})
    print("  [CREATED] Admin: username='admin', password='admin123'")
else:
    UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})
    print("  [EXISTS]  Admin user already exists, skipping.")

# -- Student users
students_data = [
    {'username': 'alice',   'first_name': 'Alice',   'last_name': 'Johnson', 'email': 'alice@example.com'},
    {'username': 'bob',     'first_name': 'Bob',     'last_name': 'Smith',   'email': 'bob@example.com'},
    {'username': 'charlie', 'first_name': 'Charlie', 'last_name': 'Brown',   'email': 'charlie@example.com'},
    {'username': 'diana',   'first_name': 'Diana',   'last_name': 'Prince',  'email': 'diana@example.com'},
]

student_objects = {}
for sdata in students_data:
    user, created = User.objects.get_or_create(username=sdata['username'])
    if created:
        user.set_password('student123')
        user.first_name = sdata['first_name']
        user.last_name  = sdata['last_name']
        user.email      = sdata['email']
        user.save()
        UserProfile.objects.get_or_create(user=user, defaults={'role': 'student'})
        print("  [CREATED] Student: username='{}', password='student123'".format(sdata['username']))
    else:
        UserProfile.objects.get_or_create(user=user, defaults={'role': 'student'})
        print("  [EXISTS]  Student '{}' already exists, skipping.".format(sdata['username']))
    student_objects[sdata['username']] = user


# ============================================================
# STEP 2: CREATE COURSES
# ============================================================
print("\n[2/5] Creating courses...")

courses_data = [
    {
        'title': 'Python Programming for Beginners',
        'description': (
            'Learn Python from scratch! This course covers the fundamental concepts of '
            'programming using Python -- one of the most popular languages in the world. '
            'Perfect for students with no prior coding experience.'
        ),
        'modules': [
            {'title': 'Introduction to Python & Setup',    'order': 1, 'duration': 45,
             'content': 'Install Python, set up VS Code, and write your first Hello World program.'},
            {'title': 'Variables and Data Types',          'order': 2, 'duration': 60,
             'content': 'Learn about integers, floats, strings, and booleans. Understand how variables store data.'},
            {'title': 'Control Flow: if/else Statements',  'order': 3, 'duration': 55,
             'content': 'Make decisions in your code using if, elif, and else statements.'},
            {'title': 'Loops: for and while',              'order': 4, 'duration': 70,
             'content': 'Repeat code efficiently using for loops and while loops. Learn break and continue.'},
            {'title': 'Functions and Scope',               'order': 5, 'duration': 65,
             'content': 'Define reusable blocks of code using functions. Understand local vs global scope.'},
        ]
    },
    {
        'title': 'Web Development with Django',
        'description': (
            'Build full-stack web applications using Django, Python\'s most popular web framework. '
            'You\'ll learn about models, views, templates, and the Django ORM.'
        ),
        'modules': [
            {'title': 'Django Installation & Project Setup', 'order': 1, 'duration': 50,
             'content': 'Install Django, create your first project, and understand the project structure.'},
            {'title': 'Models and the Django ORM',           'order': 2, 'duration': 75,
             'content': 'Define database models and interact with MySQL using Django\'s ORM.'},
            {'title': 'URL Routing and Views',               'order': 3, 'duration': 60,
             'content': 'Map URLs to view functions and return HTTP responses.'},
            {'title': 'HTML Templates and Template Tags',    'order': 4, 'duration': 65,
             'content': 'Render dynamic HTML using Django\'s template language.'},
        ]
    },
    {
        'title': 'Database Design with MySQL',
        'description': (
            'Master relational database design and SQL. Learn to create efficient schemas, '
            'write complex queries, and optimize database performance.'
        ),
        'modules': [
            {'title': 'Introduction to Databases & SQL', 'order': 1, 'duration': 55,
             'content': 'Understand what databases are and the basics of SQL syntax.'},
            {'title': 'Creating Tables and Data Types',  'order': 2, 'duration': 60,
             'content': 'Learn CREATE TABLE, data types (INT, VARCHAR, DATE), and constraints.'},
            {'title': 'SELECT Queries and Filtering',    'order': 3, 'duration': 70,
             'content': 'Write SELECT statements with WHERE, ORDER BY, GROUP BY, and HAVING.'},
        ]
    },
    {
        'title': 'Data Structures and Algorithms',
        'description': (
            'Build a strong foundation in Computer Science. Learn about arrays, linked lists, '
            'stacks, queues, trees, and essential algorithms.'
        ),
        'modules': [
            {'title': 'Arrays and Lists',    'order': 1, 'duration': 60,
             'content': 'Understand arrays, Python lists, indexing, slicing, and complexity.'},
            {'title': 'Stacks and Queues',   'order': 2, 'duration': 55,
             'content': 'Implement stack (LIFO) and queue (FIFO) data structures.'},
            {'title': 'Binary Search',       'order': 3, 'duration': 50,
             'content': 'Learn the divide-and-conquer binary search algorithm.'},
            {'title': 'Sorting Algorithms',  'order': 4, 'duration': 75,
             'content': 'Implement and compare Bubble Sort, Selection Sort, and Merge Sort.'},
        ]
    },
]

course_objects = {}
for cdata in courses_data:
    course, created = Course.objects.get_or_create(
        title=cdata['title'],
        defaults={
            'description': cdata['description'],
            'created_by': admin_user,
            'is_published': True,
        }
    )
    if created:
        for mdata in cdata['modules']:
            Module.objects.get_or_create(
                course=course,
                module_order=mdata['order'],
                defaults={
                    'title':            mdata['title'],
                    'content':          mdata['content'],
                    'duration_minutes': mdata['duration'],
                }
            )
        print("  [CREATED] '{}' ({} modules)".format(course.title, len(cdata['modules'])))
    else:
        print("  [EXISTS]  '{}' already exists, skipping.".format(course.title))
    course_objects[cdata['title']] = course


# ============================================================
# STEP 3: CREATE ENROLLMENTS
# ============================================================
print("\n[3/5] Creating enrollments...")

alice   = student_objects['alice']
bob     = student_objects['bob']
charlie = student_objects['charlie']
diana   = student_objects['diana']

python_course = course_objects['Python Programming for Beginners']
django_course = course_objects['Web Development with Django']
mysql_course  = course_objects['Database Design with MySQL']
dsa_course    = course_objects['Data Structures and Algorithms']

enrollments = [
    (alice,   python_course),
    (alice,   django_course),
    (alice,   dsa_course),
    (bob,     python_course),
    (bob,     mysql_course),
    (charlie, python_course),
    (charlie, django_course),
    (diana,   dsa_course),
    (diana,   mysql_course),
]

for student, course in enrollments:
    enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
    if created:
        print("  [CREATED] {} --> '{}'".format(student.username, course.title))


# ============================================================
# STEP 4: CREATE STUDENT PROGRESS
# ============================================================
print("\n[4/5] Adding student progress records...")

def complete_modules(student, course, num_to_complete, base_score=75.0):
    """
    Mark the first num_to_complete modules of a course as completed for student.
    Score varies slightly per module for realism.
    """
    modules = Module.objects.filter(course=course).order_by('module_order')
    for i, module in enumerate(modules):
        if i < num_to_complete:
            score = round(min(100.0, max(0.0, base_score + (i * 1.5) - 2.0)), 1)
            progress, created = StudentProgress.objects.get_or_create(
                student=student,
                module=module,
                defaults={
                    'is_completed': True,
                    'score':        score,
                    'completed_at': timezone.now(),
                }
            )
            if not created and not progress.is_completed:
                progress.is_completed = True
                progress.score        = score
                progress.completed_at = timezone.now()
                progress.save()

# Alice: Python = 100% (5/5), Django = 50% (2/4), DSA = 75% (3/4)
complete_modules(alice, python_course, 5, base_score=82.0)
complete_modules(alice, django_course, 2, base_score=78.0)
complete_modules(alice, dsa_course,    3, base_score=90.0)
print("  [DONE] Alice: Python=5/5, Django=2/4, DSA=3/4")

# Bob: Python = 100% (5/5), MySQL = 33% (1/3)
complete_modules(bob, python_course, 5, base_score=71.0)
complete_modules(bob, mysql_course,  1, base_score=68.0)
print("  [DONE] Bob: Python=5/5, MySQL=1/3")

# Charlie: Python = 60% (3/5), Django = 100% (4/4)
complete_modules(charlie, python_course, 3, base_score=75.0)
complete_modules(charlie, django_course, 4, base_score=88.0)
print("  [DONE] Charlie: Python=3/5, Django=4/4")

# Diana: DSA = 100% (4/4), MySQL = 67% (2/3)
complete_modules(diana, dsa_course,   4, base_score=94.0)
complete_modules(diana, mysql_course, 2, base_score=85.0)
print("  [DONE] Diana: DSA=4/4, MySQL=2/3")


# ============================================================
# STEP 5: AUTO-AWARD CERTIFICATES
# ============================================================
print("\n[5/5] Checking and issuing certificates...")

for student, course in enrollments:
    cert = check_and_award_certificate(student, course)
    if cert:
        progress = calculate_progress(student, course)
        print("  [CERT]  {} -- '{}' ({}%)".format(
            student.username, course.title, progress['percentage']
        ))


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("  SEED DATA COMPLETE!")
print("=" * 60)
print("""
  PLATFORM SUMMARY
  ----------------
  Courses:      {}
  Modules:      {}
  Students:     {}
  Enrollments:  {}
  Certificates: {}

  LOGIN CREDENTIALS
  -----------------
  Admin  :  admin    / admin123
  Student:  alice    / student123
  Student:  bob      / student123
  Student:  charlie  / student123
  Student:  diana    / student123

  START THE SERVER
  ----------------
  python manage.py runserver
  Then open: http://127.0.0.1:8000/
""".format(
    Course.objects.count(),
    Module.objects.count(),
    UserProfile.objects.filter(role='student').count(),
    Enrollment.objects.count(),
    Certificate.objects.filter(is_eligible=True).count(),
))
