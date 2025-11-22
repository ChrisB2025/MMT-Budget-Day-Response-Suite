"""Admin configuration for users app"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Team


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin"""
    list_display = ['username', 'email', 'display_name', 'team', 'points', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'team']
    search_fields = ['username', 'email', 'display_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('MMT Budget Suite', {
            'fields': ('display_name', 'team', 'points'),
        }),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Team admin"""
    list_display = ['name', 'total_points', 'member_count', 'created_at']
    search_fields = ['name']

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'
