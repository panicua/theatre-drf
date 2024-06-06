# Generated by Django 5.0.6 on 2024-06-06 17:30

import theatre_api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theatre_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='play',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='play',
            name='poster',
            field=models.ImageField(null=True, upload_to=theatre_api.models.play_poster_file_path),
        ),
    ]
