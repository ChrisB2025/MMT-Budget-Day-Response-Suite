"""Fact-check models"""
from django.db import models
from django.conf import settings


class FactCheckRequest(models.Model):
    """User-submitted claim for fact-checking"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('processing', 'Processing'),
        ('reviewed', 'Reviewed'),
        ('published', 'Published'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fact_check_requests'
    )
    claim_text = models.TextField(help_text='The claim to fact-check')
    context = models.TextField(blank=True, help_text='Additional context')
    timestamp_in_speech = models.CharField(
        max_length=20,
        blank=True,
        help_text='Timestamp in speech (e.g., 12:45:30)'
    )
    severity = models.IntegerField(
        help_text='User-rated severity 1-10',
        choices=[(i, str(i)) for i in range(1, 11)]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_check_requests'
        verbose_name = 'Fact-Check Request'
        verbose_name_plural = 'Fact-Check Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.claim_text[:50]}... (Severity: {self.severity})"


class FactCheckResponse(models.Model):
    """AI-generated fact-check response"""
    request = models.OneToOneField(
        FactCheckRequest,
        on_delete=models.CASCADE,
        related_name='response'
    )
    the_claim = models.TextField(help_text='Restated claim')
    the_problem = models.TextField(help_text='What is misleading')
    the_reality = models.TextField(help_text='What is actually true')
    the_evidence = models.TextField(blank=True, help_text='Supporting evidence')
    mmt_perspective = models.TextField(blank=True, help_text='MMT perspective')
    citations = models.JSONField(
        default=list,
        help_text='List of citation objects {title, url}'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_fact_checks'
    )

    class Meta:
        db_table = 'fact_check_responses'
        verbose_name = 'Fact-Check Response'
        verbose_name_plural = 'Fact-Check Responses'

    def __str__(self):
        return f"Response to: {self.request.claim_text[:50]}..."


class FactCheckUpvote(models.Model):
    """Track user upvotes for fact-check requests"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request = models.ForeignKey(FactCheckRequest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fact_check_upvotes'
        unique_together = [['user', 'request']]
        verbose_name = 'Fact-Check Upvote'
        verbose_name_plural = 'Fact-Check Upvotes'
