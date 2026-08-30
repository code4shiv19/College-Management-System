from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Faculty(models.Model):
    DESIGNATION_CHOICES = [
        ("PROF", "Professor"),
        ("ASSOC", "Associate Professor"),
        ("ASST", "Assistant Professor"),
        ("LECT", "Lecturer"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="faculty_profile"
    )
    employee_id = models.CharField(max_length=20, unique=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name="faculty_members"
    )

    designation = models.CharField(
        max_length=10,
        choices=DESIGNATION_CHOICES,
        default="LECT"
    )

    phone = models.CharField(max_length=15, blank=True)
    date_joined = models.DateField(default=timezone.now)

    photo = CloudinaryField(
        "faculty_photo",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = "Faculty"
        ordering = ["employee_id"]

    def __str__(self):
        return (
            f"{self.user.get_full_name() or self.user.username} "
            f"- {self.get_designation_display()}"
        )


class Course(models.Model):
    code = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=150)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    credits = models.PositiveSmallIntegerField(default=3)

    semester = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses_taught"
    )

    description = models.TextField(blank=True)

    cover_image = CloudinaryField("cover_image")

    class Meta:
        ordering = ["semester", "code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("GRADUATED", "Graduated"),
        ("SUSPENDED", "Suspended"),
        ("DROPPED", "Dropped"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    roll_number = models.CharField(
        max_length=20,
        unique=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name="students"
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField(blank=True)

    admission_date = models.DateField(
        default=timezone.now
    )

    current_semester = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    photo = CloudinaryField(
        "image"
    )

    class Meta:
        ordering = ["roll_number"]

    def __str__(self):
        return (
            f"{self.roll_number} - "
            f"{self.user.get_full_name() or self.user.username}"
        )


class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    enrolled_on = models.DateField(
        default=timezone.now
    )

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_on"]

    def __str__(self):
        return f"{self.student.roll_number} -> {self.course.code}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LATE", "Late"),
    ]

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField(
        default=timezone.now
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PRESENT"
    )

    marked_by = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("enrollment", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.enrollment} - {self.date} - {self.status}"


class Result(models.Model):
    GRADE_CHOICES = [
        ("A+", "A+"),
        ("A", "A"),
        ("B+", "B+"),
        ("B", "B"),
        ("C+", "C+"),
        ("C", "C"),
        ("D", "D"),
        ("F", "F"),
    ]

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="result"
    )

    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    grade = models.CharField(
        max_length=2,
        choices=GRADE_CHOICES,
        blank=True
    )

    remarks = models.CharField(
        max_length=200,
        blank=True
    )

    published_on = models.DateField(
        default=timezone.now
    )

    def save(self, *args, **kwargs):
        if not self.grade:
            self.grade = self._compute_grade()

        super().save(*args, **kwargs)

    def _compute_grade(self):
        m = float(self.marks_obtained)

        if m >= 90:
            return "A+"
        if m >= 80:
            return "A"
        if m >= 70:
            return "B+"
        if m >= 60:
            return "B"
        if m >= 50:
            return "C+"
        if m >= 40:
            return "C"
        if m >= 33:
            return "D"

        return "F"

    def __str__(self):
        return f"{self.enrollment} - {self.grade}"