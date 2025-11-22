"""Admin configuration for core app"""
from django.contrib import admin
from .models import UserAction, Achievement


@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    """User action admin"""
    list_display = ['user', 'action_type', 'action_target', 'points_earned', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username', 'action_target']
    readonly_fields = ['created_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Achievement admin"""
    list_display = ['user', 'achievement_type', 'unlocked_at']
    list_filter = ['achievement_type', 'unlocked_at']
    search_fields = ['user__username']
    readonly_fields = ['unlocked_at']
