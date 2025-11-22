# Generated migration for factcheck app

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
            name='FactCheckRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('claim_text', models.TextField(help_text='The claim to fact-check')),
                ('context', models.TextField(blank=True, help_text='Additional context')),
                ('timestamp_in_speech', models.CharField(blank=True, help_text='Timestamp in speech (e.g., 12:45:30)', max_length=20)),
                ('severity', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')], help_text='User-rated severity 1-10')),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('processing', 'Processing'), ('reviewed', 'Reviewed'), ('published', 'Published')], default='submitted', max_length=20)),
                ('upvotes', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fact_check_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Fact-Check Request',
                'verbose_name_plural': 'Fact-Check Requests',
                'db_table': 'fact_check_requests',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['status'], name='fact_check_requests_status_idx'),
                    models.Index(fields=['user'], name='fact_check_requests_user_idx'),
                    models.Index(fields=['created_at'], name='fact_check_requests_created_at_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='FactCheckUpvote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='factcheck.factcheckrequest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Fact-Check Upvote',
                'verbose_name_plural': 'Fact-Check Upvotes',
                'db_table': 'fact_check_upvotes',
            },
        ),
        migrations.CreateModel(
            name='FactCheckResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('the_claim', models.TextField(help_text='Restated claim')),
                ('the_problem', models.TextField(help_text='What is misleading')),
                ('the_reality', models.TextField(help_text='What is actually true')),
                ('the_evidence', models.TextField(blank=True, help_text='Supporting evidence')),
                ('mmt_perspective', models.TextField(blank=True, help_text='MMT perspective')),
                ('citations', models.JSONField(default=list, help_text='List of citation objects {title, url}')),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='response', to='factcheck.factcheckrequest')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_fact_checks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Fact-Check Response',
                'verbose_name_plural': 'Fact-Check Responses',
                'db_table': 'fact_check_responses',
            },
        ),
        migrations.AlterUniqueTogether(
            name='factcheckupvote',
            unique_together={('user', 'request')},
        ),
    ]
