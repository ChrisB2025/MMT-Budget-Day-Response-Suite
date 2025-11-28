"""Django admin configuration for article critique models."""
from django.contrib import admin
from .models import ArticleSubmission, ArticleCritique, QuickResponse, ArticleUpvote, ArticleContentCache


@admin.register(ArticleSubmission)
class ArticleSubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'publication', 'status', 'user', 'created_at', 'view_count']
    list_filter = ['status', 'publication', 'extraction_method', 'is_paywalled', 'created_at']
    search_fields = ['title', 'author', 'original_url', 'extracted_text']
    readonly_fields = ['share_id', 'created_at', 'updated_at', 'view_count']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Source', {
            'fields': ('user', 'original_url', 'archive_url', 'extraction_method')
        }),
        ('Article Metadata', {
            'fields': ('title', 'author', 'publication', 'publication_date')
        }),
        ('Content', {
            'fields': ('extracted_text', 'is_paywalled'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Tracking', {
            'fields': ('share_id', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ArticleCritique)
class ArticleCritiqueAdmin(admin.ModelAdmin):
    list_display = ['article', 'accuracy_rating', 'confidence_score', 'generated_at']
    list_filter = ['accuracy_rating', 'generated_at']
    search_fields = ['summary', 'mmt_analysis', 'article__title']
    raw_id_fields = ['article']

    fieldsets = (
        ('Article', {
            'fields': ('article',)
        }),
        ('Summary & Rating', {
            'fields': ('summary', 'accuracy_rating', 'confidence_score')
        }),
        ('Claims & Analysis', {
            'fields': ('key_claims', 'mmt_analysis', 'quick_rebuttal'),
        }),
        ('Errors & Issues', {
            'fields': ('factual_errors', 'framing_issues', 'missing_context'),
            'classes': ('collapse',)
        }),
        ('Corrections', {
            'fields': ('recommended_corrections', 'citations'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuickResponse)
class QuickResponseAdmin(admin.ModelAdmin):
    list_display = ['article', 'response_type', 'char_count', 'created_at']
    list_filter = ['response_type', 'created_at']
    search_fields = ['content', 'article__title']
    raw_id_fields = ['article']


@admin.register(ArticleUpvote)
class ArticleUpvoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at']
    list_filter = ['created_at']
    raw_id_fields = ['user', 'article']


@admin.register(ArticleContentCache)
class ArticleContentCacheAdmin(admin.ModelAdmin):
    list_display = ['url', 'fetched_at', 'expires_at', 'is_expired']
    list_filter = ['fetched_at']
    search_fields = ['url']
    readonly_fields = ['url_hash', 'fetched_at']

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
