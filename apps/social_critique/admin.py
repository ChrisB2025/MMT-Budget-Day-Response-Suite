"""Admin configuration for social critique models"""
from django.contrib import admin
from .models import (
    SocialMediaCritique,
    CritiqueResponse,
    ShareableReply,
    CritiqueUpvote,
    ContentCache
)


@admin.register(SocialMediaCritique)
class SocialMediaCritiqueAdmin(admin.ModelAdmin):
    list_display = ['id', 'platform', 'source_title', 'user', 'status', 'view_count', 'created_at']
    list_filter = ['status', 'platform', 'created_at']
    search_fields = ['url', 'source_title', 'source_author', 'source_text']
    readonly_fields = ['share_id', 'created_at', 'updated_at', 'view_count']
    raw_id_fields = ['user']

    fieldsets = (
        ('Source', {
            'fields': ('url', 'platform', 'user')
        }),
        ('Fetched Content', {
            'fields': ('source_title', 'source_author', 'source_text',
                      'source_description', 'source_thumbnail_url', 'source_publish_date'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Metadata', {
            'fields': ('share_id', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CritiqueResponse)
class CritiqueResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'critique', 'accuracy_rating', 'confidence_score', 'generated_at']
    list_filter = ['accuracy_rating', 'generated_at']
    search_fields = ['summary', 'mmt_analysis', 'key_misconceptions']
    readonly_fields = ['generated_at']
    raw_id_fields = ['critique']


@admin.register(ShareableReply)
class ShareableReplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'critique', 'reply_type', 'platform_target', 'char_count', 'is_within_limit']
    list_filter = ['reply_type', 'platform_target']
    search_fields = ['content']
    raw_id_fields = ['critique']


@admin.register(CritiqueUpvote)
class CritiqueUpvoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'critique', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['user', 'critique']


@admin.register(ContentCache)
class ContentCacheAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'fetched_at', 'expires_at', 'is_expired']
    list_filter = ['fetched_at', 'expires_at']
    search_fields = ['url']
    readonly_fields = ['url_hash', 'fetched_at']
