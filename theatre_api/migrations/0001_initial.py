# Generated by Django 5.0.6 on 2024-06-06 16:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TheatreHall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('rows', models.PositiveIntegerField()),
                ('seats_in_row', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Play',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('actors', models.ManyToManyField(blank=True, related_name='plays', to='theatre_api.actor')),
                ('genres', models.ManyToManyField(blank=True, related_name='plays', to='theatre_api.genre')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_time', models.DateTimeField()),
                ('play', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to='theatre_api.play')),
                ('theatre_hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to='theatre_api.theatrehall')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.PositiveIntegerField()),
                ('seat', models.PositiveIntegerField()),
                ('performance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='theatre_api.performance')),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='theatre_api.reservation')),
            ],
            options={
                'ordering': ['row', 'seat'],
                'unique_together': {('performance', 'row', 'seat')},
            },
        ),
    ]
