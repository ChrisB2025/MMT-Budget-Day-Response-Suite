"""Social media critique models"""
import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse


class SocialMediaCritique(models.Model):
    """User-submitted social media URL for MMT critique"""

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('fetching', 'Fetching Content'),
        ('analyzing', 'Analyzing Content'),
        ('generating_replies', 'Generating Replies'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PLATFORM_CHOICES = [
        ('twitter', 'Twitter/X'),
        ('youtube', 'YouTube'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('linkedin', 'LinkedIn'),
        ('threads', 'Threads'),
        ('bluesky', 'Bluesky'),
        ('mastodon', 'Mastodon'),
        ('reddit', 'Reddit'),
        ('other', 'Other'),
    ]

    # Unique share ID for public URLs
    share_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_critiques'
    )

    # Source information
    url = models.URLField(max_length=2048, help_text='URL to the social media post')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='other')

    # Fetched content
    source_title = models.CharField(max_length=500, blank=True, help_text='Title of the content')
    source_author = models.CharField(max_length=200, blank=True, help_text='Author/channel name')
    source_text = models.TextField(blank=True, help_text='Extracted text content')
    source_description = models.TextField(blank=True, help_text='Description or summary')
    source_thumbnail_url = models.URLField(max_length=2048, blank=True)
    source_publish_date = models.DateTimeField(null=True, blank=True)

    # Manual transcript (for YouTube when automatic extraction fails)
    manual_transcript = models.TextField(blank=True, help_text='User-provided transcript for YouTube videos')

    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    error_message = models.TextField(blank=True, help_text='Error details if failed')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # View tracking
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'social_media_critiques'
        verbose_name = 'Social Media Critique'
        verbose_name_plural = 'Social Media Critiques'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='social_crit_status_idx'),
            models.Index(fields=['user'], name='social_crit_user_idx'),
            models.Index(fields=['share_id'], name='social_crit_share_id_idx'),
            models.Index(fields=['platform'], name='social_crit_platform_idx'),
            models.Index(fields=['created_at'], name='social_crit_created_idx'),
        ]

    def __str__(self):
        return f"{self.get_platform_display()}: {self.source_title or self.url[:50]}"

    def get_absolute_url(self):
        return reverse('social_critique:detail', kwargs={'share_id': self.share_id})

    def get_share_url(self):
        """Get the public shareable URL"""
        return reverse('social_critique:public_view', kwargs={'share_id': self.share_id})

    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class CritiqueResponse(models.Model):
    """AI-generated critique response for social media content"""

    critique = models.OneToOneField(
        SocialMediaCritique,
        on_delete=models.CASCADE,
        related_name='response'
    )

    # Structured critique content
    summary = models.TextField(help_text='Brief summary of the content and main claims')
    claims_identified = models.JSONField(
        default=list,
        help_text='List of economic claims identified in the content'
    )
    mmt_analysis = models.TextField(help_text='MMT perspective analysis')
    key_misconceptions = models.TextField(help_text='Key economic misconceptions identified')
    reality_check = models.TextField(help_text='What the evidence actually shows')
    recommended_reading = models.JSONField(
        default=list,
        help_text='List of recommended resources {title, url, description}'
    )

    # Overall assessment
    RATING_CHOICES = [
        ('accurate', 'Economically Accurate'),
        ('mostly_accurate', 'Mostly Accurate'),
        ('mixed', 'Mixed Accuracy'),
        ('misleading', 'Misleading'),
        ('false', 'Economically False'),
    ]
    accuracy_rating = models.CharField(max_length=20, choices=RATING_CHOICES, default='mixed')
    confidence_score = models.FloatField(
        default=0.0,
        help_text='AI confidence in the analysis (0-1)'
    )

    # Citations
    citations = models.JSONField(
        default=list,
        help_text='List of citations {title, url}'
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_critique_responses'
        verbose_name = 'Critique Response'
        verbose_name_plural = 'Critique Responses'

    def __str__(self):
        return f"Response for: {self.critique.source_title or self.critique.url[:30]}"


class ShareableReply(models.Model):
    """Pre-generated reply content for social media sharing"""

    REPLY_TYPE_CHOICES = [
        ('short', 'Short Reply'),      # Single post within char limits
        ('thread', 'Thread'),          # Multi-post thread
        ('summary', 'Summary Card'),   # Brief summary for sharing
    ]

    critique = models.ForeignKey(
        SocialMediaCritique,
        on_delete=models.CASCADE,
        related_name='shareable_replies'
    )

    reply_type = models.CharField(max_length=20, choices=REPLY_TYPE_CHOICES)

    # Platform-specific content
    platform_target = models.CharField(
        max_length=20,
        choices=SocialMediaCritique.PLATFORM_CHOICES,
        help_text='Target platform for this reply format'
    )

    # Reply content
    content = models.TextField(help_text='The reply text content')
    thread_parts = models.JSONField(
        default=list,
        blank=True,
        help_text='For threads: list of individual post texts'
    )

    # Character counts for validation
    char_count = models.IntegerField(default=0)

    # Link to full critique
    include_link = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_critique_shareable_replies'
        verbose_name = 'Shareable Reply'
        verbose_name_plural = 'Shareable Replies'
        unique_together = [['critique', 'reply_type', 'platform_target']]

    def __str__(self):
        return f"{self.get_reply_type_display()} for {self.get_platform_target_display()}"

    @property
    def is_within_limit(self):
        """Check if content is within platform character limits"""
        limits = {
            'twitter': 280,
            'threads': 500,
            'bluesky': 300,
            'mastodon': 500,
            'linkedin': 3000,
            'facebook': 63206,
            'instagram': 2200,
            'tiktok': 2200,
            'youtube': 10000,
            'reddit': 10000,
            'other': 10000,
        }
        return self.char_count <= limits.get(self.platform_target, 10000)


class CritiqueUpvote(models.Model):
    """Track user upvotes for critiques"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    critique = models.ForeignKey(SocialMediaCritique, on_delete=models.CASCADE, related_name='upvotes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_critique_upvotes'
        unique_together = [['user', 'critique']]
        verbose_name = 'Critique Upvote'
        verbose_name_plural = 'Critique Upvotes'


class ContentCache(models.Model):
    """Cache fetched content to avoid re-fetching"""
    url_hash = models.CharField(max_length=64, unique=True, help_text='SHA256 hash of URL')
    url = models.URLField(max_length=2048)
    content = models.JSONField(help_text='Cached content data')
    fetched_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text='Cache expiration time')

    class Meta:
        db_table = 'social_critique_content_cache'
        verbose_name = 'Content Cache'
        verbose_name_plural = 'Content Cache Entries'
        indexes = [
            models.Index(fields=['url_hash'], name='social_cache_url_hash_idx'),
            models.Index(fields=['expires_at'], name='social_cache_expires_idx'),
        ]

    def __str__(self):
        return f"Cache: {self.url[:50]}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
