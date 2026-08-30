from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("students/", views.student_list, name="student_list"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("faculty/", views.faculty_list, name="faculty_list"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("manage/students/add/", views.manage_student_create, name="student_add"),
    path("manage/students/<int:pk>/edit/", views.manage_student_edit, name="student_edit"),
    path("manage/students/<int:pk>/delete/", views.manage_student_delete, name="student_delete"),
    path("manage/faculty/add/", views.manage_faculty_create, name="faculty_add"),
    path("manage/faculty/<int:pk>/edit/", views.manage_faculty_edit, name="faculty_edit"),
    path("manage/faculty/<int:pk>/delete/", views.manage_faculty_delete, name="faculty_delete"),
    path("manage/courses/add/", views.manage_course_create, name="course_add"),
    path("manage/courses/<int:pk>/edit/", views.manage_course_edit, name="course_edit"),
    path("manage/courses/<int:pk>/delete/", views.manage_course_delete, name="course_delete"),
]
