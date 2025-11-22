"""User models"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Team(models.Model):
    """Team for competition (future feature)"""
    name = models.CharField(max_length=100)
    total_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Extended user model with MMT Budget Suite specific fields"""
    display_name = models.CharField(max_length=100, blank=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    points = models.IntegerField(default=0)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['team']),
        ]

    def __str__(self):
        return self.display_name or self.username

    def save(self, *args, **kwargs):
        # Set display_name from username if not provided
        if not self.display_name:
            self.display_name = self.username
        super().save(*args, **kwargs)
