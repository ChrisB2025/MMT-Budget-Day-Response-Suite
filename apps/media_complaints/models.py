"""Media Complaints models for tracking and responding to economic misinformation"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class MediaOutlet(models.Model):
    """Media outlets and organizations for complaint targeting"""
    MEDIA_TYPE_CHOICES = [
        ('tv', 'Television'),
        ('radio', 'Radio'),
        ('print', 'Print'),
        ('online', 'Online'),
        ('social', 'Social Media'),
    ]

    name = models.CharField(max_length=200, unique=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    contact_email = models.EmailField(help_text='Primary contact email for complaints')
    complaints_dept_email = models.EmailField(blank=True, help_text='Specific complaints department email')
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    # Useful for letter generation
    regulator = models.CharField(max_length=100, blank=True, help_text='e.g., Ofcom, IPSO')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'media_outlets'
        verbose_name = 'Media Outlet'
        verbose_name_plural = 'Media Outlets'
        ordering = ['name']
        indexes = [
            models.Index(fields=['media_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_media_type_display()})"


class Complaint(models.Model):
    """User-submitted complaint about economic misinformation in media"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Letter Generation'),
        ('generated', 'Letter Generated'),
        ('sent', 'Sent'),
        ('responded', 'Responded To'),
    ]

    SEVERITY_CHOICES = [
        (1, 'Minor'),
        (2, 'Moderate'),
        (3, 'Serious'),
        (4, 'Very Serious'),
        (5, 'Severe'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='media_complaints'
    )
    outlet = models.ForeignKey(
        MediaOutlet,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    # Incident details
    incident_date = models.DateField(help_text='Date of the misinformation')
    programme_name = models.CharField(max_length=200, help_text='Programme, show, or article name')
    presenter_journalist = models.CharField(
        max_length=200,
        blank=True,
        help_text='Presenter, journalist, or author'
    )
    timestamp = models.CharField(
        max_length=20,
        blank=True,
        help_text='Timestamp in programme (e.g., 14:23)'
    )

    # The misinformation
    claim_description = models.TextField(
        help_text='Describe the misinformation or misleading claim'
    )
    context = models.TextField(
        blank=True,
        help_text='Additional context about the incident'
    )
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=3)

    # User preferences for letter
    TONE_CHOICES = [
        ('professional', 'Professional'),
        ('academic', 'Academic'),
        ('passionate', 'Passionate'),
    ]
    preferred_tone = models.CharField(
        max_length=20,
        choices=TONE_CHOICES,
        default='professional'
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # Track how many complaints have been filed for this incident (for variation)
    incident_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text='Hash of incident for tracking duplicate complaints'
    )
    complaint_number_for_incident = models.IntegerField(
        default=1,
        help_text='Which complaint number is this for this incident'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'media_complaints'
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['outlet']),
            models.Index(fields=['status']),
            models.Index(fields=['incident_date']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Complaint to {self.outlet.name} by {self.user.display_name} - {self.incident_date}"

    def save(self, *args, **kwargs):
        """Generate incident hash on save"""
        if not self.incident_hash:
            import hashlib
            incident_key = f"{self.outlet.id}_{self.incident_date}_{self.programme_name}_{self.presenter_journalist}"
            self.incident_hash = hashlib.sha256(incident_key.encode()).hexdigest()

            # Count existing complaints for this incident
            existing_count = Complaint.objects.filter(
                incident_hash=self.incident_hash
            ).count()
            self.complaint_number_for_incident = existing_count + 1

        super().save(*args, **kwargs)


class ComplaintLetter(models.Model):
    """AI-generated complaint letter with variation tracking"""
    VARIATION_STRATEGY_CHOICES = [
        ('correction', 'Request Correction'),
        ('training', 'Request Staff Training'),
        ('policy', 'Request Policy Review'),
        ('investigation', 'Request Investigation'),
        ('accountability', 'Emphasize Accountability'),
    ]

    complaint = models.OneToOneField(
        Complaint,
        on_delete=models.CASCADE,
        related_name='letter'
    )

    # Letter content
    subject = models.CharField(max_length=200)
    body = models.TextField(help_text='Full letter body')

    # Generation metadata
    variation_strategy = models.CharField(
        max_length=30,
        choices=VARIATION_STRATEGY_CHOICES,
        help_text='Which rhetorical strategy was used'
    )
    tone_used = models.CharField(max_length=20, help_text='Tone used in generation')

    # MMT talking points included
    mmt_points_included = models.JSONField(
        default=list,
        help_text='List of MMT points addressed in the letter'
    )

    # Sending status
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_to_email = models.EmailField(blank=True)

    # Response tracking
    response_received = models.BooleanField(default=False)
    response_date = models.DateField(null=True, blank=True)
    response_summary = models.TextField(blank=True)

    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'complaint_letters'
        verbose_name = 'Complaint Letter'
        verbose_name_plural = 'Complaint Letters'
        ordering = ['-generated_at']

    def __str__(self):
        return f"Letter for complaint {self.complaint.id} - {self.variation_strategy}"

    def mark_as_sent(self, email_address):
        """Mark letter as sent"""
        self.sent_at = timezone.now()
        self.sent_to_email = email_address
        self.complaint.status = 'sent'
        self.save()
        self.complaint.save()


class ComplaintStats(models.Model):
    """Track complaint statistics per user (for gamification)"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaint_stats'
    )

    total_complaints_filed = models.IntegerField(default=0)
    complaints_sent = models.IntegerField(default=0)
    responses_received = models.IntegerField(default=0)

    # Achievements
    first_complaint_at = models.DateTimeField(null=True, blank=True)
    most_active_outlet = models.ForeignKey(
        MediaOutlet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='top_complainers'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'complaint_stats'
        verbose_name = 'Complaint Statistics'
        verbose_name_plural = 'Complaint Statistics'

    def __str__(self):
        return f"{self.user.display_name} - {self.total_complaints_filed} complaints"

    def update_stats(self):
        """Refresh statistics from complaint data"""
        self.total_complaints_filed = self.user.media_complaints.count()
        self.complaints_sent = self.user.media_complaints.filter(status='sent').count()
        self.responses_received = self.user.media_complaints.filter(
            letter__response_received=True
        ).count()

        if not self.first_complaint_at and self.total_complaints_filed > 0:
            first_complaint = self.user.media_complaints.order_by('created_at').first()
            if first_complaint:
                self.first_complaint_at = first_complaint.created_at

        # Find most complained about outlet
        from django.db.models import Count
        top_outlet = self.user.media_complaints.values('outlet').annotate(
            count=Count('outlet')
        ).order_by('-count').first()

        if top_outlet:
            self.most_active_outlet_id = top_outlet['outlet']

        self.save()


class OutletSuggestion(models.Model):
    """User suggestions for new media outlets"""
    STATUS_CHOICES = [
        ('pending', 'Pending Research'),
        ('researched', 'Research Complete'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('created', 'Outlet Created'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='outlet_suggestions'
    )

    # Suggested outlet details
    name = models.CharField(max_length=200)
    media_type = models.CharField(max_length=20, choices=MediaOutlet.MEDIA_TYPE_CHOICES)
    website = models.URLField(blank=True, help_text='Official website')
    description = models.TextField(blank=True, help_text='Why this outlet should be added')

    # AI-researched information
    suggested_contact_email = models.EmailField(blank=True, help_text='AI-suggested contact email')
    suggested_complaints_email = models.EmailField(blank=True, help_text='AI-suggested complaints email')
    suggested_regulator = models.CharField(max_length=100, blank=True, help_text='AI-suggested regulator')
    research_notes = models.TextField(blank=True, help_text='AI research findings')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text='Admin review notes')

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_outlet_suggestions'
    )

    class Meta:
        db_table = 'outlet_suggestions'
        verbose_name = 'Outlet Suggestion'
        verbose_name_plural = 'Outlet Suggestions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.name} suggested by {self.user.display_name}"
