# Generated by Django 5.1.4 on 2025-03-18 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_alter_job_working_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='processing_time',
            field=models.CharField(default='3 weeks', max_length=50),
        ),
    ]
