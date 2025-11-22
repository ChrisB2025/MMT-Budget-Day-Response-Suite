# Generated migration for core app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('bingo_mark', 'Bingo Mark'), ('bingo_complete', 'Bingo Complete'), ('factcheck_submit', 'Fact-Check Submit'), ('factcheck_upvote', 'Fact-Check Upvote'), ('rebuttal_download', 'Rebuttal Download')], max_length=50)),
                ('action_target', models.CharField(blank=True, help_text='ID or identifier of the target', max_length=100)),
                ('points_earned', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Action',
                'verbose_name_plural': 'User Actions',
                'db_table': 'user_actions',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user'], name='user_actions_user_idx'),
                    models.Index(fields=['action_type'], name='user_actions_action_type_idx'),
                    models.Index(fields=['created_at'], name='user_actions_created_at_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achievement_type', models.CharField(choices=[('early_bird', 'Early Bird'), ('bingo_champion', 'Bingo Champion'), ('fact_finder', 'Fact Finder'), ('super_contributor', 'Super Contributor')], max_length=50)),
                ('achievement_data', models.JSONField(default=dict, help_text='Additional metadata about the achievement')),
                ('unlocked_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Achievement',
                'verbose_name_plural': 'Achievements',
                'db_table': 'achievements',
                'ordering': ['-unlocked_at'],
                'indexes': [
                    models.Index(fields=['user'], name='achievements_user_idx'),
                    models.Index(fields=['achievement_type'], name='achievements_achievement_type_idx'),
                ],
            },
        ),
        migrations.AlterUniqueTogether(
            name='achievement',
            unique_together={('user', 'achievement_type')},
        ),
    ]
