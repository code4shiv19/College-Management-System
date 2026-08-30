from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="cover_image",
            field=models.ImageField(blank=True, null=True, upload_to="course_covers/"),
        ),
    ]
