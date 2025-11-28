# Generated migration for article_critique app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('original_url', models.URLField(blank=True, help_text='Original article URL', max_length=2048)),
                ('archive_url', models.URLField(blank=True, help_text='Archive URL used for extraction', max_length=2048)),
                ('extraction_method', models.CharField(choices=[('direct', 'Direct Fetch'), ('archive_ph', 'archive.ph'), ('removepaywall', 'RemovePaywall'), ('wayback', 'Wayback Machine'), ('12ft', '12ft.io'), ('manual', 'Manual Paste')], default='direct', max_length=20)),
                ('title', models.CharField(blank=True, help_text='Article title', max_length=500)),
                ('author', models.CharField(blank=True, help_text='Article author(s)', max_length=300)),
                ('publication', models.CharField(choices=[('guardian', 'The Guardian'), ('bbc', 'BBC'), ('independent', 'The Independent'), ('ft', 'Financial Times'), ('times', 'The Times'), ('telegraph', 'The Telegraph'), ('economist', 'The Economist'), ('spectator', 'The Spectator'), ('newstatesman', 'New Statesman'), ('mirror', 'Mirror'), ('daily_mail', 'Daily Mail'), ('express', 'Daily Express'), ('sky_news', 'Sky News'), ('itv_news', 'ITV News'), ('reuters', 'Reuters'), ('bloomberg', 'Bloomberg'), ('wsj', 'Wall Street Journal'), ('nyt', 'New York Times'), ('other', 'Other')], default='other', help_text='Publication source', max_length=30)),
                ('publication_date', models.DateField(blank=True, help_text='Publication date', null=True)),
                ('extracted_text', models.TextField(blank=True, help_text='Extracted article text')),
                ('is_paywalled', models.BooleanField(default=False, help_text='Was paywall detected')),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('extracting', 'Extracting Content'), ('analyzing', 'Analyzing Content'), ('generating', 'Generating Responses'), ('completed', 'Completed'), ('failed', 'Failed')], default='submitted', max_length=20)),
                ('error_message', models.TextField(blank=True, help_text='Error details if failed')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('view_count', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Article Submission',
                'verbose_name_plural': 'Article Submissions',
                'db_table': 'article_submissions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ArticleContentCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_hash', models.CharField(help_text='SHA256 hash of URL', max_length=64, unique=True)),
                ('url', models.URLField(max_length=2048)),
                ('content', models.JSONField(help_text='Cached content data')),
                ('fetched_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(help_text='Cache expiration time')),
            ],
            options={
                'verbose_name': 'Article Content Cache',
                'verbose_name_plural': 'Article Content Cache Entries',
                'db_table': 'article_content_cache',
            },
        ),
        migrations.CreateModel(
            name='QuickResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_type', models.CharField(choices=[('tweet', 'Tweet'), ('thread', 'Thread'), ('letter', 'Letter to Editor'), ('comment', 'Article Comment')], max_length=20)),
                ('content', models.TextField(help_text='The response text')),
                ('thread_parts', models.JSONField(blank=True, default=list, help_text='For threads: list of individual post texts')),
                ('char_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quick_responses', to='article_critique.articlesubmission')),
            ],
            options={
                'verbose_name': 'Quick Response',
                'verbose_name_plural': 'Quick Responses',
                'db_table': 'article_quick_responses',
                'unique_together': {('article', 'response_type')},
            },
        ),
        migrations.CreateModel(
            name='ArticleUpvote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upvotes', to='article_critique.articlesubmission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Article Upvote',
                'verbose_name_plural': 'Article Upvotes',
                'db_table': 'article_critique_upvotes',
                'unique_together': {('user', 'article')},
            },
        ),
        migrations.CreateModel(
            name='ArticleCritique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField(help_text='Brief summary of the article and main issues')),
                ('key_claims', models.JSONField(default=list, help_text='List of key economic claims in the article')),
                ('mmt_analysis', models.TextField(help_text='MMT perspective on the article claims')),
                ('factual_errors', models.JSONField(default=list, help_text='List of factual errors {claim, problem, correction}')),
                ('framing_issues', models.JSONField(default=list, help_text='List of framing issues {issue, problematic_framing, better_framing}')),
                ('missing_context', models.TextField(blank=True, help_text='Important context the article omits')),
                ('recommended_corrections', models.TextField(blank=True, help_text='Suggested corrections for the article')),
                ('quick_rebuttal', models.TextField(blank=True, help_text='Short rebuttal paragraph')),
                ('accuracy_rating', models.CharField(choices=[('accurate', 'Economically Accurate'), ('mostly_accurate', 'Mostly Accurate'), ('mixed', 'Mixed Accuracy'), ('misleading', 'Misleading'), ('false', 'Economically False')], default='mixed', max_length=20)),
                ('confidence_score', models.FloatField(default=0.5, help_text='AI confidence in analysis (0-1)')),
                ('citations', models.JSONField(default=list, help_text='List of citations {title, url}')),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='critique', to='article_critique.articlesubmission')),
            ],
            options={
                'verbose_name': 'Article Critique',
                'verbose_name_plural': 'Article Critiques',
                'db_table': 'article_critiques',
            },
        ),
        migrations.AddIndex(
            model_name='articlesubmission',
            index=models.Index(fields=['status'], name='article_sub_status_idx'),
        ),
        migrations.AddIndex(
            model_name='articlesubmission',
            index=models.Index(fields=['user'], name='article_sub_user_idx'),
        ),
        migrations.AddIndex(
            model_name='articlesubmission',
            index=models.Index(fields=['share_id'], name='article_sub_share_id_idx'),
        ),
        migrations.AddIndex(
            model_name='articlesubmission',
            index=models.Index(fields=['publication'], name='article_sub_pub_idx'),
        ),
        migrations.AddIndex(
            model_name='articlesubmission',
            index=models.Index(fields=['created_at'], name='article_sub_created_idx'),
        ),
        migrations.AddIndex(
            model_name='articlecontentcache',
            index=models.Index(fields=['url_hash'], name='article_cache_url_idx'),
        ),
        migrations.AddIndex(
            model_name='articlecontentcache',
            index=models.Index(fields=['expires_at'], name='article_cache_exp_idx'),
        ),
    ]
