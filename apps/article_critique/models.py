"""Database models for article critique functionality."""
import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse


class ArticleSubmission(models.Model):
    """User-submitted article for MMT critique."""

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('extracting', 'Extracting Content'),
        ('analyzing', 'Analyzing Content'),
        ('generating', 'Generating Responses'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    EXTRACTION_METHOD_CHOICES = [
        ('direct', 'Direct Fetch'),
        ('archive_ph', 'archive.ph'),
        ('removepaywall', 'RemovePaywall'),
        ('wayback', 'Wayback Machine'),
        ('12ft', '12ft.io'),
        ('manual', 'Manual Paste'),
    ]

    PUBLICATION_CHOICES = [
        ('guardian', 'The Guardian'),
        ('bbc', 'BBC'),
        ('independent', 'The Independent'),
        ('ft', 'Financial Times'),
        ('times', 'The Times'),
        ('telegraph', 'The Telegraph'),
        ('economist', 'The Economist'),
        ('spectator', 'The Spectator'),
        ('newstatesman', 'New Statesman'),
        ('mirror', 'Mirror'),
        ('daily_mail', 'Daily Mail'),
        ('express', 'Daily Express'),
        ('sky_news', 'Sky News'),
        ('itv_news', 'ITV News'),
        ('reuters', 'Reuters'),
        ('bloomberg', 'Bloomberg'),
        ('wsj', 'Wall Street Journal'),
        ('nyt', 'New York Times'),
        ('other', 'Other'),
    ]

    # Unique share ID for public URLs
    share_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='article_submissions'
    )

    # Source information
    original_url = models.URLField(max_length=2048, blank=True, help_text='Original article URL')
    archive_url = models.URLField(max_length=2048, blank=True, help_text='Archive URL used for extraction')
    extraction_method = models.CharField(
        max_length=20,
        choices=EXTRACTION_METHOD_CHOICES,
        default='direct'
    )

    # Article metadata
    title = models.CharField(max_length=500, blank=True, help_text='Article title')
    author = models.CharField(max_length=300, blank=True, help_text='Article author(s)')
    publication = models.CharField(
        max_length=30,
        choices=PUBLICATION_CHOICES,
        default='other',
        help_text='Publication source'
    )
    publication_date = models.DateField(null=True, blank=True, help_text='Publication date')

    # Content
    extracted_text = models.TextField(blank=True, help_text='Extracted article text')
    is_paywalled = models.BooleanField(default=False, help_text='Was paywall detected')

    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    error_message = models.TextField(blank=True, help_text='Error details if failed')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # View tracking
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'article_submissions'
        verbose_name = 'Article Submission'
        verbose_name_plural = 'Article Submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='article_sub_status_idx'),
            models.Index(fields=['user'], name='article_sub_user_idx'),
            models.Index(fields=['share_id'], name='article_sub_share_id_idx'),
            models.Index(fields=['publication'], name='article_sub_pub_idx'),
            models.Index(fields=['created_at'], name='article_sub_created_idx'),
        ]

    def __str__(self):
        return f"{self.title or self.original_url[:50]}"

    def get_absolute_url(self):
        return reverse('article_critique:detail', kwargs={'share_id': self.share_id})

    def get_share_url(self):
        """Get the public shareable URL"""
        return reverse('article_critique:public_view', kwargs={'share_id': self.share_id})

    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def get_publication_display_name(self):
        """Get publication name or custom name"""
        for choice_value, choice_label in self.PUBLICATION_CHOICES:
            if choice_value == self.publication:
                return choice_label
        return self.publication


class ArticleCritique(models.Model):
    """AI-generated MMT critique of an article."""

    article = models.OneToOneField(
        ArticleSubmission,
        on_delete=models.CASCADE,
        related_name='critique'
    )

    # Executive summary
    summary = models.TextField(help_text='Brief summary of the article and main issues')

    # Structured critique content
    key_claims = models.JSONField(
        default=list,
        help_text='List of key economic claims in the article'
    )

    # MMT analysis
    mmt_analysis = models.TextField(help_text='MMT perspective on the article claims')

    # Errors and issues
    factual_errors = models.JSONField(
        default=list,
        help_text='List of factual errors {claim, problem, correction}'
    )
    framing_issues = models.JSONField(
        default=list,
        help_text='List of framing issues {issue, problematic_framing, better_framing}'
    )

    # Missing context
    missing_context = models.TextField(blank=True, help_text='Important context the article omits')

    # Recommended corrections
    recommended_corrections = models.TextField(
        blank=True,
        help_text='Suggested corrections for the article'
    )

    # Quick rebuttal for immediate response
    quick_rebuttal = models.TextField(blank=True, help_text='Short rebuttal paragraph')

    # Rating
    RATING_CHOICES = [
        ('accurate', 'Economically Accurate'),
        ('mostly_accurate', 'Mostly Accurate'),
        ('mixed', 'Mixed Accuracy'),
        ('misleading', 'Misleading'),
        ('false', 'Economically False'),
    ]
    accuracy_rating = models.CharField(max_length=20, choices=RATING_CHOICES, default='mixed')
    confidence_score = models.FloatField(default=0.5, help_text='AI confidence in analysis (0-1)')

    # Citations and references
    citations = models.JSONField(
        default=list,
        help_text='List of citations {title, url}'
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_critiques'
        verbose_name = 'Article Critique'
        verbose_name_plural = 'Article Critiques'

    def __str__(self):
        return f"Critique of: {self.article.title or 'Unknown Article'}"


class QuickResponse(models.Model):
    """Pre-generated response content for sharing."""

    RESPONSE_TYPE_CHOICES = [
        ('tweet', 'Tweet'),
        ('thread', 'Thread'),
        ('letter', 'Letter to Editor'),
        ('comment', 'Article Comment'),
    ]

    article = models.ForeignKey(
        ArticleSubmission,
        on_delete=models.CASCADE,
        related_name='quick_responses'
    )

    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPE_CHOICES)

    # Response content
    content = models.TextField(help_text='The response text')
    thread_parts = models.JSONField(
        default=list,
        blank=True,
        help_text='For threads: list of individual post texts'
    )

    # Character count
    char_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_quick_responses'
        verbose_name = 'Quick Response'
        verbose_name_plural = 'Quick Responses'
        unique_together = [['article', 'response_type']]

    def __str__(self):
        return f"{self.get_response_type_display()} for {self.article.title[:30]}"


class ArticleUpvote(models.Model):
    """Track user upvotes for article critiques."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(ArticleSubmission, on_delete=models.CASCADE, related_name='upvotes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_critique_upvotes'
        unique_together = [['user', 'article']]
        verbose_name = 'Article Upvote'
        verbose_name_plural = 'Article Upvotes'


class ArticleContentCache(models.Model):
    """Cache extracted article content to avoid re-fetching."""

    url_hash = models.CharField(max_length=64, unique=True, help_text='SHA256 hash of URL')
    url = models.URLField(max_length=2048)
    content = models.JSONField(help_text='Cached content data')
    fetched_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text='Cache expiration time')

    class Meta:
        db_table = 'article_content_cache'
        verbose_name = 'Article Content Cache'
        verbose_name_plural = 'Article Content Cache Entries'
        indexes = [
            models.Index(fields=['url_hash'], name='article_cache_url_idx'),
            models.Index(fields=['expires_at'], name='article_cache_exp_idx'),
        ]

    def __str__(self):
        return f"Cache: {self.url[:50]}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
