# Generated migration for social_critique app

import uuid
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
            name='SocialMediaCritique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('url', models.URLField(help_text='URL to the social media post', max_length=2048)),
                ('platform', models.CharField(choices=[('twitter', 'Twitter/X'), ('youtube', 'YouTube'), ('facebook', 'Facebook'), ('instagram', 'Instagram'), ('tiktok', 'TikTok'), ('linkedin', 'LinkedIn'), ('threads', 'Threads'), ('bluesky', 'Bluesky'), ('mastodon', 'Mastodon'), ('reddit', 'Reddit'), ('other', 'Other')], default='other', max_length=20)),
                ('source_title', models.CharField(blank=True, help_text='Title of the content', max_length=500)),
                ('source_author', models.CharField(blank=True, help_text='Author/channel name', max_length=200)),
                ('source_text', models.TextField(blank=True, help_text='Extracted text content')),
                ('source_description', models.TextField(blank=True, help_text='Description or summary')),
                ('source_thumbnail_url', models.URLField(blank=True, max_length=2048)),
                ('source_publish_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('fetching', 'Fetching Content'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='submitted', max_length=20)),
                ('error_message', models.TextField(blank=True, help_text='Error details if failed')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('view_count', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_critiques', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Social Media Critique',
                'verbose_name_plural': 'Social Media Critiques',
                'db_table': 'social_media_critiques',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ContentCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_hash', models.CharField(help_text='SHA256 hash of URL', max_length=64, unique=True)),
                ('url', models.URLField(max_length=2048)),
                ('content', models.JSONField(help_text='Cached content data')),
                ('fetched_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(help_text='Cache expiration time')),
            ],
            options={
                'verbose_name': 'Content Cache',
                'verbose_name_plural': 'Content Cache Entries',
                'db_table': 'social_critique_content_cache',
            },
        ),
        migrations.CreateModel(
            name='CritiqueUpvote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('critique', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upvotes', to='social_critique.socialmediacritique')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Critique Upvote',
                'verbose_name_plural': 'Critique Upvotes',
                'db_table': 'social_critique_upvotes',
                'unique_together': {('user', 'critique')},
            },
        ),
        migrations.CreateModel(
            name='CritiqueResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField(help_text='Brief summary of the content and main claims')),
                ('claims_identified', models.JSONField(default=list, help_text='List of economic claims identified in the content')),
                ('mmt_analysis', models.TextField(help_text='MMT perspective analysis')),
                ('key_misconceptions', models.TextField(help_text='Key economic misconceptions identified')),
                ('reality_check', models.TextField(help_text='What the evidence actually shows')),
                ('recommended_reading', models.JSONField(default=list, help_text='List of recommended resources {title, url, description}')),
                ('accuracy_rating', models.CharField(choices=[('accurate', 'Economically Accurate'), ('mostly_accurate', 'Mostly Accurate'), ('mixed', 'Mixed Accuracy'), ('misleading', 'Misleading'), ('false', 'Economically False')], default='mixed', max_length=20)),
                ('confidence_score', models.FloatField(default=0.0, help_text='AI confidence in the analysis (0-1)')),
                ('citations', models.JSONField(default=list, help_text='List of citations {title, url}')),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('critique', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='response', to='social_critique.socialmediacritique')),
            ],
            options={
                'verbose_name': 'Critique Response',
                'verbose_name_plural': 'Critique Responses',
                'db_table': 'social_critique_responses',
            },
        ),
        migrations.CreateModel(
            name='ShareableReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_type', models.CharField(choices=[('short', 'Short Reply'), ('thread', 'Thread'), ('summary', 'Summary Card')], max_length=20)),
                ('platform_target', models.CharField(choices=[('twitter', 'Twitter/X'), ('youtube', 'YouTube'), ('facebook', 'Facebook'), ('instagram', 'Instagram'), ('tiktok', 'TikTok'), ('linkedin', 'LinkedIn'), ('threads', 'Threads'), ('bluesky', 'Bluesky'), ('mastodon', 'Mastodon'), ('reddit', 'Reddit'), ('other', 'Other')], help_text='Target platform for this reply format', max_length=20)),
                ('content', models.TextField(help_text='The reply text content')),
                ('thread_parts', models.JSONField(blank=True, default=list, help_text='For threads: list of individual post texts')),
                ('char_count', models.IntegerField(default=0)),
                ('include_link', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('critique', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shareable_replies', to='social_critique.socialmediacritique')),
            ],
            options={
                'verbose_name': 'Shareable Reply',
                'verbose_name_plural': 'Shareable Replies',
                'db_table': 'social_critique_shareable_replies',
                'unique_together': {('critique', 'reply_type', 'platform_target')},
            },
        ),
        migrations.AddIndex(
            model_name='socialmediacritique',
            index=models.Index(fields=['status'], name='social_crit_status_idx'),
        ),
        migrations.AddIndex(
            model_name='socialmediacritique',
            index=models.Index(fields=['user'], name='social_crit_user_idx'),
        ),
        migrations.AddIndex(
            model_name='socialmediacritique',
            index=models.Index(fields=['share_id'], name='social_crit_share_id_idx'),
        ),
        migrations.AddIndex(
            model_name='socialmediacritique',
            index=models.Index(fields=['platform'], name='social_crit_platform_idx'),
        ),
        migrations.AddIndex(
            model_name='socialmediacritique',
            index=models.Index(fields=['created_at'], name='social_crit_created_idx'),
        ),
        migrations.AddIndex(
            model_name='contentcache',
            index=models.Index(fields=['url_hash'], name='social_cache_url_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='contentcache',
            index=models.Index(fields=['expires_at'], name='social_cache_expires_idx'),
        ),
    ]
