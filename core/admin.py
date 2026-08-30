from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Faculty, Course, Student, Enrollment, Attendance, Result


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("photo_preview", "employee_id", "user", "department", "designation", "date_joined")
    list_filter = ("department", "designation")
    search_fields = ("employee_id", "user__first_name", "user__last_name", "user__username")
    readonly_fields = ("photo_preview",)

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:45px;height:45px;object-fit:cover;border-radius:10px;" />', obj.photo.url)
        return "—"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("cover_preview", "code", "name", "department", "semester", "credits", "faculty")
    list_filter = ("department", "semester")
    search_fields = ("code", "name")
    readonly_fields = ("cover_preview",)

    @admin.display(description="Cover")
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="width:70px;height:42px;object-fit:cover;border-radius:8px;" />', obj.cover_image.url)
        return "—"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("photo_preview", "roll_number", "user", "department", "current_semester", "status")
    list_filter = ("department", "current_semester", "status")
    search_fields = ("roll_number", "user__first_name", "user__last_name", "user__username")
    readonly_fields = ("photo_preview",)

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:45px;height:45px;object-fit:cover;border-radius:10px;" />', obj.photo.url)
        return "—"


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_on")
    list_filter = ("course",)
    search_fields = ("student__roll_number", "course__code")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "date", "status", "marked_by")
    list_filter = ("status", "date")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "marks_obtained", "grade", "published_on")
    list_filter = ("grade",)
