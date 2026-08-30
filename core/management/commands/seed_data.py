import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Department, Faculty, Course, Student, Enrollment, Result


class Command(BaseCommand):
    help = "Seed the database with sample departments, faculty, students, courses, and results."

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample data...")

        departments_data = [
            ("Computer Science", "CS"),
            ("Electronics", "EC"),
            ("Mechanical", "ME"),
            ("Business Administration", "BA"),
        ]
        departments = []
        for name, code in departments_data:
            dept, _ = Department.objects.get_or_create(code=code, defaults={"name": name})
            departments.append(dept)

        faculty_names = [
            ("Anita", "Sharma"), ("Ravi", "Kumar"), ("Meera", "Iyer"), ("Sanjay", "Verma"),
        ]
        faculty_list = []
        for i, (first, last) in enumerate(faculty_names, start=1):
            username = f"faculty{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "email": f"{username}@college.edu"},
            )
            if created:
                user.set_password("password123")
                user.save()
            faculty, _ = Faculty.objects.get_or_create(
                user=user,
                defaults={
                    "employee_id": f"EMP00{i}",
                    "department": departments[i % len(departments)],
                    "designation": random.choice(["PROF", "ASSOC", "ASST", "LECT"]),
                    "date_joined": date.today() - timedelta(days=365 * i),
                },
            )
            faculty_list.append(faculty)

        courses_data = [
            ("CS101", "Introduction to Programming", 0, 1, 4),
            ("CS201", "Data Structures", 0, 2, 4),
            ("CS301", "Database Systems", 0, 3, 3),
            ("EC101", "Basic Electronics", 1, 1, 3),
            ("ME101", "Engineering Mechanics", 2, 1, 3),
            ("BA101", "Principles of Management", 3, 1, 3),
        ]
        courses = []
        for i, (code, name, dept_idx, semester, credits) in enumerate(courses_data):
            course, _ = Course.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department": departments[dept_idx],
                    "semester": semester,
                    "credits": credits,
                    "faculty": faculty_list[i % len(faculty_list)],
                },
            )
            courses.append(course)

        student_names = [
            ("Aarav", "Gupta"), ("Priya", "Singh"), ("Rohan", "Mehta"), ("Neha", "Patel"),
            ("Karan", "Joshi"), ("Divya", "Nair"),
        ]
        students = []
        for i, (first, last) in enumerate(student_names, start=1):
            username = f"student{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "email": f"{username}@college.edu"},
            )
            if created:
                user.set_password("password123")
                user.save()
            student, _ = Student.objects.get_or_create(
                user=user,
                defaults={
                    "roll_number": f"2026CS{i:03d}",
                    "department": departments[i % len(departments)],
                    "current_semester": random.choice([1, 2, 3]),
                    "admission_date": date.today() - timedelta(days=200 * i),
                },
            )
            students.append(student)

        for student in students:
            for course in random.sample(courses, k=3):
                enrollment, _ = Enrollment.objects.get_or_create(student=student, course=course)
                Result.objects.get_or_create(
                    enrollment=enrollment,
                    defaults={"marks_obtained": random.randint(40, 98)},
                )

        self.stdout.write(self.style.SUCCESS(
            "Done. Created sample admin login: admin/admin123 (if you ran createsuperuser separately), "
            "faculty logins: faculty1-4/password123, student logins: student1-6/password123."
        ))
