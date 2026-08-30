from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import StudentPhotoForm, FacultyPhotoForm
from .models import Student, Faculty, Course, Department, Enrollment, Result


def _profile_for(user):
    if hasattr(user, "student_profile"):
        return "student", user.student_profile
    if hasattr(user, "faculty_profile"):
        return "faculty", user.faculty_profile
    return "admin", None


@login_required
def dashboard(request):
    context = {
        "student_count": Student.objects.count(),
        "faculty_count": Faculty.objects.count(),
        "course_count": Course.objects.count(),
        "department_count": Department.objects.count(),
        "recent_students": Student.objects.select_related("user", "department").order_by("-id")[:6],
        "featured_courses": Course.objects.select_related("department", "faculty").order_by("semester", "code")[:6],
    }

    role, profile = _profile_for(request.user)
    context["role"] = role
    if role == "student":
        context["student"] = profile
        context["enrollments"] = profile.enrollments.select_related("course", "result")
    elif role == "faculty":
        context["faculty"] = profile
        context["courses_taught"] = profile.courses_taught.all()
    return render(request, "core/dashboard.html", context)


@login_required
def profile(request):
    role, profile_obj = _profile_for(request.user)
    if role == "admin":
        messages.info(request, "Admin accounts can manage profile images from the Django Admin panel.")
        return redirect("core:dashboard")

    if request.method == "POST":
        form_class = StudentPhotoForm if role == "student" else FacultyPhotoForm
        form = form_class(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile photo was updated successfully.")
            return redirect("core:profile")
    else:
        form_class = StudentPhotoForm if role == "student" else FacultyPhotoForm
        form = form_class(instance=profile_obj)

    return render(request, "core/profile.html", {"profile": profile_obj, "role": role, "form": form})


@login_required
def student_list(request):
    students = Student.objects.select_related("user", "department").all()
    return render(request, "core/student_list.html", {"students": students})


@login_required
def faculty_list(request):
    faculty = Faculty.objects.select_related("user", "department").all()
    return render(request, "core/faculty_list.html", {"faculty": faculty})


@login_required
def course_list(request):
    courses = Course.objects.select_related("department", "faculty").all()
    return render(request, "core/course_list.html", {"courses": courses})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollments = course.enrollments.select_related("student", "result").all()
    return render(request, "core/course_detail.html", {"course": course, "enrollments": enrollments})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.select_related("course", "result").all()
    return render(request, "core/student_detail.html", {"student": student, "enrollments": enrollments})

from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .forms import StudentManageForm, FacultyManageForm, CourseManageForm


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


@staff_required
def manage_student_create(request):
    form = StudentManageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student added successfully.")
        return redirect("core:student_list")
    return render(request, "core/manage_form.html", {"form": form, "title": "Add Student", "subtitle": "Create a student profile with login details and photo.", "icon": "bi-person-plus", "back_url": "core:student_list", "entity": "student"})


@staff_required
def manage_student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentManageForm(request.POST or None, request.FILES or None, instance=student)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student updated successfully.")
        return redirect("core:student_detail", pk=pk)
    return render(request, "core/manage_form.html", {"form": form, "title": "Edit Student", "subtitle": "Update profile, academic details or photo.", "icon": "bi-person-gear", "back_url": "core:student_detail", "back_args": [pk], "entity": "student", "object": student})


@staff_required
def manage_student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        name = student.user.get_full_name() or student.roll_number
        student.user.delete()
        messages.success(request, f"Student {name} was removed.")
        return redirect("core:student_list")
    return render(request, "core/confirm_delete.html", {"object": student, "title": "Remove Student", "type": "student", "back_url": "core:student_detail", "back_args": [pk]})


@staff_required
def manage_faculty_create(request):
    form = FacultyManageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Faculty member added successfully.")
        return redirect("core:faculty_list")
    return render(request, "core/manage_form.html", {"form": form, "title": "Add Faculty", "subtitle": "Create a faculty profile, login and photo.", "icon": "bi-person-badge-fill", "back_url": "core:faculty_list", "entity": "faculty"})


@staff_required
def manage_faculty_edit(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    form = FacultyManageForm(request.POST or None, request.FILES or None, instance=faculty)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Faculty member updated successfully.")
        return redirect("core:faculty_list")
    return render(request, "core/manage_form.html", {"form": form, "title": "Edit Faculty", "subtitle": "Update faculty details, designation or photo.", "icon": "bi-person-gear", "back_url": "core:faculty_list", "entity": "faculty", "object": faculty})


@staff_required
def manage_faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == "POST":
        name = faculty.user.get_full_name() or faculty.employee_id
        faculty.user.delete()
        messages.success(request, f"Faculty member {name} was removed.")
        return redirect("core:faculty_list")
    return render(request, "core/confirm_delete.html", {"object": faculty, "title": "Remove Faculty", "type": "faculty", "back_url": "core:faculty_list"})


@staff_required
def manage_course_create(request):
    form = CourseManageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course added successfully.")
        return redirect("core:course_list")
    return render(request, "core/manage_form.html", {"form": form, "title": "Add Course", "subtitle": "Create a course and optionally add a cover image.", "icon": "bi-journal-plus", "back_url": "core:course_list", "entity": "course"})


@staff_required
def manage_course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseManageForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course updated successfully.")
        return redirect("core:course_detail", pk=pk)
    return render(request, "core/manage_form.html", {"form": form, "title": "Edit Course", "subtitle": "Update course information or cover image.", "icon": "bi-journal-code", "back_url": "core:course_detail", "back_args": [pk], "entity": "course", "object": course})


@staff_required
def manage_course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        name = course.name
        course.delete()
        messages.success(request, f"Course {name} was removed.")
        return redirect("core:course_list")
    return render(request, "core/confirm_delete.html", {"object": course, "title": "Remove Course", "type": "course", "back_url": "core:course_detail", "back_args": [pk]})
