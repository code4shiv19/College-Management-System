# CampusHub — College Management System

A modern Django college management system for students, faculty and courses.

## Features
- Professional responsive dashboard UI
- Student, faculty and course CRUD from the web interface
- Profile photos and course cover images
- Drag-and-drop image upload with instant preview
- JPG, PNG and WebP validation (5 MB maximum)
- Student/faculty search
- Course catalogue and detail pages
- Django admin for advanced management
- SQLite database for easy local setup

## Run locally

```bash
python -m venv venv
# Windows
venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Photo upload

Uploaded images are stored in the project's `media/` folder. The project includes a media URL route so uploaded photos display immediately in the dashboard, lists and profile pages.

If an image was uploaded before and the browser still shows an old/broken image, hard-refresh the page with `Ctrl + F5`.

For production hosting, use persistent media storage (for example Cloudinary or an object-storage service) instead of relying on the local `media/` folder.
