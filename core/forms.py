from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from .models import Student, Faculty, Course, Department


class PhotoValidationMixin:
    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Please choose an image smaller than 5 MB.")
        if photo:
            try:
                from PIL import Image
                image = Image.open(photo)
                if image.width < 200 or image.height < 200:
                    raise forms.ValidationError("Please use an image at least 200×200 pixels.")
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise forms.ValidationError("Only JPG, PNG or WebP images are allowed.")
            except forms.ValidationError:
                raise
            except Exception:
                raise forms.ValidationError("Please upload a valid JPG, PNG or WebP image.")
        return photo


class StudentPhotoForm(PhotoValidationMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = ["photo"]
        widgets = {"photo": forms.ClearableFileInput(attrs={"class": "form-control form-control-lg", "accept": "image/jpeg,image/png,image/webp"})}


class FacultyPhotoForm(PhotoValidationMixin, forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ["photo"]
        widgets = {"photo": forms.ClearableFileInput(attrs={"class": "form-control form-control-lg", "accept": "image/jpeg,image/png,image/webp"})}


class StudentManageForm(PhotoValidationMixin, forms.Form):
    first_name = forms.CharField(max_length=150, label="First name")
    last_name = forms.CharField(max_length=150, required=False, label="Last name")
    email = forms.EmailField(required=False)
    username = forms.CharField(max_length=150, label="Login username")
    password = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False), help_text="Required when creating a new student.")
    roll_number = forms.CharField(max_length=20)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(choices=[("", "Select gender")] + Student.GENDER_CHOICES, required=False)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    admission_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    current_semester = forms.IntegerField(min_value=1, max_value=8, initial=1)
    status = forms.ChoiceField(choices=Student.STATUS_CHOICES, initial="ACTIVE")
    photo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "class": "form-control"}))

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select): field.widget.attrs["class"] = "form-select"
            elif not isinstance(field.widget, forms.FileInput): field.widget.attrs["class"] = "form-control"
        if instance:
            u = instance.user
            for field, value in {
                "first_name": u.first_name, "last_name": u.last_name, "email": u.email, "username": u.username,
                "roll_number": instance.roll_number, "department": instance.department, "date_of_birth": instance.date_of_birth,
                "gender": instance.gender, "phone": instance.phone, "address": instance.address, "admission_date": instance.admission_date,
                "current_semester": instance.current_semester, "status": instance.status,
            }.items():
                self.fields[field].initial = value

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.instance and not password:
            raise forms.ValidationError("Password is required when creating a student.")
        return password

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username=username)
        if self.instance:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError("This username is already in use.")
        return username

    def clean_roll_number(self):
        roll = self.cleaned_data["roll_number"]
        qs = Student.objects.filter(roll_number=roll)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This roll number already exists.")
        return roll

    def clean_photo(self):
        return PhotoValidationMixin.clean_photo(self)

    @transaction.atomic
    def save(self):
        data = self.cleaned_data
        if self.instance:
            user = self.instance.user
            profile = self.instance
        else:
            user = User()
            profile = Student(user=user)
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]
        user.username = data["username"]
        if data.get("password"):
            user.set_password(data["password"])
        elif not self.instance:
            user.set_unusable_password()
        user.save()
        profile.roll_number = data["roll_number"]
        profile.department = data["department"]
        profile.date_of_birth = data["date_of_birth"]
        profile.gender = data["gender"]
        profile.phone = data["phone"]
        profile.address = data["address"]
        profile.admission_date = data["admission_date"] or profile.admission_date
        profile.current_semester = data["current_semester"]
        profile.status = data["status"]
        if data.get("photo"):
            profile.photo = data["photo"]
        profile.save()
        return profile


class FacultyManageForm(PhotoValidationMixin, forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    username = forms.CharField(max_length=150, label="Login username")
    password = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False), help_text="Required when creating a new faculty member.")
    employee_id = forms.CharField(max_length=20)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    designation = forms.ChoiceField(choices=Faculty.DESIGNATION_CHOICES, initial="LECT")
    phone = forms.CharField(max_length=15, required=False)
    date_joined = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    photo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "class": "form-control"}))

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select): field.widget.attrs["class"] = "form-select"
            elif not isinstance(field.widget, forms.FileInput): field.widget.attrs["class"] = "form-control"
        if instance:
            u = instance.user
            for field, value in {"first_name": u.first_name, "last_name": u.last_name, "email": u.email, "username": u.username,
                                  "employee_id": instance.employee_id, "department": instance.department, "designation": instance.designation,
                                  "phone": instance.phone, "date_joined": instance.date_joined}.items():
                self.fields[field].initial = value

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.instance and not password:
            raise forms.ValidationError("Password is required when creating a faculty member.")
        return password

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username=username)
        if self.instance:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError("This username is already in use.")
        return username

    def clean_employee_id(self):
        value = self.cleaned_data["employee_id"]
        qs = Faculty.objects.filter(employee_id=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This employee ID already exists.")
        return value

    def clean_photo(self):
        return PhotoValidationMixin.clean_photo(self)

    @transaction.atomic
    def save(self):
        data = self.cleaned_data
        if self.instance:
            user = self.instance.user
            profile = self.instance
        else:
            user = User()
            profile = Faculty(user=user)
        user.first_name, user.last_name, user.email, user.username = data["first_name"], data["last_name"], data["email"], data["username"]
        if data.get("password"):
            user.set_password(data["password"])
        elif not self.instance:
            user.set_unusable_password()
        user.save()
        profile.employee_id, profile.department, profile.designation = data["employee_id"], data["department"], data["designation"]
        profile.phone, profile.date_joined = data["phone"], (data["date_joined"] or profile.date_joined)
        if data.get("photo"):
            profile.photo = data["photo"]
        profile.save()
        return profile


class CourseManageForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "name", "department", "credits", "semester", "faculty", "description", "cover_image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "cover_image": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "class": "form-control"}),
        }

    def clean_cover_image(self):
        image = self.cleaned_data.get("cover_image")
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Please choose an image smaller than 5 MB.")
        if image:
            try:
                from PIL import Image
                opened = Image.open(image)
                if opened.width < 400 or opened.height < 200:
                    raise forms.ValidationError("Please use a cover image at least 400×200 pixels.")
            except forms.ValidationError:
                raise
            except Exception:
                raise forms.ValidationError("Please upload a valid image.")
        return image
