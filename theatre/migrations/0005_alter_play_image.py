# Generated by Django 5.1.6 on 2025-02-25 12:44

import theatre.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theatre", "0004_play_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="play",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to=theatre.models.play_image_upload_path
            ),
        ),
    ]
