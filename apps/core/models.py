"""Core models for shared functionality"""
from django.db import models
from django.conf import settings


class UserAction(models.Model):
    """Track user actions for analytics and gamification"""
    ACTION_TYPES = [
        ('bingo_mark', 'Bingo Mark'),
        ('bingo_complete', 'Bingo Complete'),
        ('factcheck_submit', 'Fact-Check Submit'),
        ('factcheck_upvote', 'Fact-Check Upvote'),
        ('rebuttal_download', 'Rebuttal Download'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_target = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID or identifier of the target'
    )
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_actions'
        verbose_name = 'User Action'
        verbose_name_plural = 'User Actions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.display_name} - {self.action_type}"


class Achievement(models.Model):
    """User achievements"""
    ACHIEVEMENT_TYPES = [
        ('early_bird', 'Early Bird'),
        ('bingo_champion', 'Bingo Champion'),
        ('fact_finder', 'Fact Finder'),
        ('super_contributor', 'Super Contributor'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    achievement_data = models.JSONField(
        default=dict,
        help_text='Additional metadata about the achievement'
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'achievements'
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
        unique_together = [['user', 'achievement_type']]
        ordering = ['-unlocked_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['achievement_type']),
        ]

    def __str__(self):
        return f"{self.user.display_name} - {self.achievement_type}"
