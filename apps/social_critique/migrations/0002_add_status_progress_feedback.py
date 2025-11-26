# Generated migration for social_critique app

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_critique', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmediacritique',
            name='status',
            field=models.CharField(
                choices=[
                    ('submitted', 'Submitted'),
                    ('fetching', 'Fetching Content'),
                    ('analyzing', 'Analyzing Content'),
                    ('generating_replies', 'Generating Replies'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                ],
                default='submitted',
                max_length=20
            ),
        ),
    ]
