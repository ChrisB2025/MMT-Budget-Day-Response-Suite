# Generated migration for social_critique app

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_critique', '0002_add_status_progress_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialmediacritique',
            name='manual_transcript',
            field=models.TextField(blank=True, help_text='User-provided transcript for YouTube videos'),
        ),
    ]
