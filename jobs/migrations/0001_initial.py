# Generated by Django 5.1.4 on 2025-03-11 23:39

import django.core.validators
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
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('flag_url', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('category', models.CharField(choices=[('Technical', 'Technical'), ('Soft', 'Soft Skills'), ('Language', 'Language')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('commission_fee', models.DecimalField(decimal_places=2, default=80000, max_digits=10)),
                ('salary_range', models.CharField(blank=True, max_length=50)),
                ('job_type', models.CharField(choices=[('Full-Time', 'Full-Time'), ('Part-Time', 'Part-Time'), ('Freelance', 'Freelance')], max_length=50)),
                ('industry', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('experience_level', models.CharField(choices=[('Entry', 'Entry Level'), ('Mid', 'Mid Level'), ('Senior', 'Senior Level'), ('Executive', 'Executive Level')], max_length=50)),
                ('remote_friendly', models.BooleanField(default=False)),
                ('accommodation_available', models.BooleanField(default=True)),
                ('transport', models.BooleanField(default=True)),
                ('jobs_for_couples', models.BooleanField(default=True)),
                ('vacancy_number', models.IntegerField(default=30)),
                ('min_salary', models.IntegerField(blank=True, null=True)),
                ('max_salary', models.IntegerField(blank=True, null=True)),
                ('application_deadline', models.DateField(blank=True, null=True)),
                ('company_rating', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.country')),
                ('posted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('required_skills', models.ManyToManyField(blank=True, to='jobs.skill')),
            ],
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Applied', 'Applied'), ('Screening', 'Screening'), ('Interview', 'Interview'), ('Offer', 'Offer'), ('Rejected', 'Rejected')], max_length=50)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('cover_letter', models.TextField(blank=True)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.job')),
            ],
        ),
    ]
