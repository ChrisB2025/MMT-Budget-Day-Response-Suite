"""Admin configuration for fact-check app"""
from django.contrib import admin
from .models import (
    FactCheckRequest, FactCheckResponse, FactCheckUpvote,
    UserProfile, UserBadge, UserFollow, ClaimComment,
    ClaimOfTheDay, ClaimOfTheMinute
)


class FactCheckResponseInline(admin.StackedInline):
    """Inline admin for fact-check responses"""
    model = FactCheckResponse
    extra = 0
    readonly_fields = ['generated_at']


@admin.register(FactCheckRequest)
class FactCheckRequestAdmin(admin.ModelAdmin):
    """Fact-check request admin"""
    list_display = ['id', 'claim_preview', 'user', 'severity', 'status', 'upvotes', 'created_at']
    list_filter = ['status', 'severity', 'created_at']
    search_fields = ['claim_text', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'upvotes']
    inlines = [FactCheckResponseInline]

    def claim_preview(self, obj):
        return obj.claim_text[:100] + '...' if len(obj.claim_text) > 100 else obj.claim_text
    claim_preview.short_description = 'Claim'


@admin.register(FactCheckResponse)
class FactCheckResponseAdmin(admin.ModelAdmin):
    """Fact-check response admin"""
    list_display = ['id', 'request', 'generated_at', 'reviewed_at', 'reviewed_by']
    list_filter = ['generated_at', 'reviewed_at']
    search_fields = ['request__claim_text', 'the_claim']
    readonly_fields = ['generated_at']


@admin.register(FactCheckUpvote)
class FactCheckUpvoteAdmin(admin.ModelAdmin):
    """Fact-check upvote admin"""
    list_display = ['user', 'request', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'request__claim_text']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin"""
    list_display = ['user', 'level', 'total_claims_submitted', 'total_upvotes_earned', 'experience_points']
    list_filter = ['level', 'created_at']
    search_fields = ['user__username', 'user__display_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """User badge admin"""
    list_display = ['user', 'badge_type', 'earned_at']
    list_filter = ['badge_type', 'earned_at']
    search_fields = ['user__username']


@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    """User follow admin"""
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']


@admin.register(ClaimComment)
class ClaimCommentAdmin(admin.ModelAdmin):
    """Claim comment admin"""
    list_display = ['user', 'request', 'text_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'text']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


@admin.register(ClaimOfTheDay)
class ClaimOfTheDayAdmin(admin.ModelAdmin):
    """Claim of the day admin"""
    list_display = ['request', 'featured_date', 'created_at']
    list_filter = ['featured_date']
    search_fields = ['request__claim_text']


@admin.register(ClaimOfTheMinute)
class ClaimOfTheMinuteAdmin(admin.ModelAdmin):
    """Claim of the minute admin"""
    list_display = ['request', 'minute_timestamp', 'upvotes_at_time']
    list_filter = ['minute_timestamp']
    search_fields = ['request__claim_text']
