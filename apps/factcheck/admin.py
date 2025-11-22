"""Admin configuration for fact-check app"""
from django.contrib import admin
from .models import FactCheckRequest, FactCheckResponse, FactCheckUpvote


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
