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


class UserProfile(models.Model):
    """Extended user profile for fact-checkers with stats and achievements"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='factcheck_profile'
    )

    # Stats
    total_claims_submitted = models.IntegerField(default=0)
    total_upvotes_earned = models.IntegerField(default=0)
    claims_fact_checked = models.IntegerField(default=0)  # Claims that got responses
    severity_accuracy_score = models.FloatField(default=0.0)  # 0-100

    # Level system
    LEVEL_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='bronze')
    experience_points = models.IntegerField(default=0)

    # Competition stats
    hot_streak_count = models.IntegerField(default=0)  # Current consecutive submissions
    max_hot_streak = models.IntegerField(default=0)  # Personal best
    claims_of_the_minute = models.IntegerField(default=0)  # Times awarded
    claims_of_the_day = models.IntegerField(default=0)  # Times featured

    # Social
    bio = models.TextField(blank=True, max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_check_user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.display_name}'s Profile"

    def calculate_level(self):
        """Calculate level based on experience points"""
        if self.experience_points >= 1000:
            return 'platinum'
        elif self.experience_points >= 500:
            return 'gold'
        elif self.experience_points >= 200:
            return 'silver'
        return 'bronze'

    def update_stats(self):
        """Update profile stats based on user activity"""
        self.total_claims_submitted = self.user.fact_check_requests.count()
        self.claims_fact_checked = self.user.fact_check_requests.filter(
            status__in=['reviewed', 'published']
        ).count()
        self.total_upvotes_earned = sum(
            req.upvotes for req in self.user.fact_check_requests.all()
        )
        self.level = self.calculate_level()
        self.save()


class UserBadge(models.Model):
    """Achievements and badges for fact-checkers"""
    BADGE_TYPES = [
        ('first_claim', 'First Claim Submitted'),
        ('verified_expert', 'Verified Expert'),
        ('hot_streak_5', 'Hot Streak: 5 in a row'),
        ('hot_streak_10', 'Hot Streak: 10 in a row'),
        ('claim_of_day', 'Claim of the Day'),
        ('claim_of_minute', 'Claim of the Minute'),
        ('upvote_king', '100 Upvotes Earned'),
        ('severity_master', 'Severity Accuracy 90%+'),
        ('prolific_checker', '50 Claims Submitted'),
        ('legendary_checker', '100 Claims Submitted'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='factcheck_badges'
    )
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fact_check_user_badges'
        unique_together = [['user', 'badge_type']]
        verbose_name = 'User Badge'
        verbose_name_plural = 'User Badges'
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.display_name} - {self.get_badge_type_display()}"


class UserFollow(models.Model):
    """Track user follows for social features"""
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='factcheck_following'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='factcheck_followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fact_check_user_follows'
        unique_together = [['follower', 'following']]
        verbose_name = 'User Follow'
        verbose_name_plural = 'User Follows'

    def __str__(self):
        return f"{self.follower.display_name} follows {self.following.display_name}"


class ClaimComment(models.Model):
    """Comments on fact-check requests"""
    request = models.ForeignKey(
        FactCheckRequest,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='factcheck_comments'
    )
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fact_check_comments'
        verbose_name = 'Claim Comment'
        verbose_name_plural = 'Claim Comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.display_name} on {self.request.id}"


class ClaimOfTheDay(models.Model):
    """Featured claim of the day"""
    request = models.ForeignKey(
        FactCheckRequest,
        on_delete=models.CASCADE,
        related_name='daily_features'
    )
    featured_date = models.DateField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fact_check_claim_of_day'
        verbose_name = 'Claim of the Day'
        verbose_name_plural = 'Claims of the Day'
        ordering = ['-featured_date']

    def __str__(self):
        return f"Claim of the Day: {self.featured_date}"


class ClaimOfTheMinute(models.Model):
    """Track highest upvoted claim per minute during speech"""
    request = models.ForeignKey(
        FactCheckRequest,
        on_delete=models.CASCADE,
        related_name='minute_features'
    )
    minute_timestamp = models.DateTimeField()  # Rounded to the minute
    upvotes_at_time = models.IntegerField()

    class Meta:
        db_table = 'fact_check_claim_of_minute'
        verbose_name = 'Claim of the Minute'
        verbose_name_plural = 'Claims of the Minute'
        ordering = ['-minute_timestamp']
        indexes = [
            models.Index(fields=['minute_timestamp']),
        ]

    def __str__(self):
        return f"Claim of Minute: {self.minute_timestamp}"
