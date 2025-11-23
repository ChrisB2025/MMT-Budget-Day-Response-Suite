"""Admin configuration for media complaints"""
from django.contrib import admin
from .models import MediaOutlet, Complaint, ComplaintLetter, ComplaintStats


@admin.register(MediaOutlet)
class MediaOutletAdmin(admin.ModelAdmin):
    """Admin for media outlets"""
    list_display = ['name', 'media_type', 'contact_email', 'regulator', 'is_active', 'created_at']
    list_filter = ['media_type', 'is_active', 'regulator']
    search_fields = ['name', 'description']
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'media_type', 'description')
        }),
        ('Contact Details', {
            'fields': ('contact_email', 'complaints_dept_email', 'website', 'regulator')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    """Admin for complaints"""
    list_display = [
        'id',
        'user',
        'outlet',
        'incident_date',
        'programme_name',
        'severity',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'severity', 'outlet', 'incident_date', 'preferred_tone']
    search_fields = ['claim_description', 'programme_name', 'presenter_journalist', 'user__display_name']
    readonly_fields = ['incident_hash', 'complaint_number_for_incident', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'status')
        }),
        ('Incident Details', {
            'fields': (
                'outlet',
                'incident_date',
                'programme_name',
                'presenter_journalist',
                'timestamp'
            )
        }),
        ('Complaint Content', {
            'fields': ('claim_description', 'context', 'severity', 'preferred_tone')
        }),
        ('System Information', {
            'fields': (
                'incident_hash',
                'complaint_number_for_incident',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'outlet')


@admin.register(ComplaintLetter)
class ComplaintLetterAdmin(admin.ModelAdmin):
    """Admin for complaint letters"""
    list_display = [
        'id',
        'complaint',
        'variation_strategy',
        'tone_used',
        'sent_at',
        'response_received',
        'generated_at'
    ]
    list_filter = ['variation_strategy', 'tone_used', 'response_received', 'sent_at']
    search_fields = ['subject', 'body', 'complaint__programme_name']
    readonly_fields = ['generated_at', 'updated_at']
    ordering = ['-generated_at']

    fieldsets = (
        ('Letter Content', {
            'fields': ('complaint', 'subject', 'body')
        }),
        ('Generation Details', {
            'fields': (
                'variation_strategy',
                'tone_used',
                'mmt_points_included',
                'generated_at',
                'updated_at'
            )
        }),
        ('Sending Status', {
            'fields': ('sent_at', 'sent_to_email')
        }),
        ('Response Tracking', {
            'fields': ('response_received', 'response_date', 'response_summary')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('complaint', 'complaint__outlet')


@admin.register(ComplaintStats)
class ComplaintStatsAdmin(admin.ModelAdmin):
    """Admin for complaint statistics"""
    list_display = [
        'user',
        'total_complaints_filed',
        'complaints_sent',
        'responses_received',
        'first_complaint_at',
        'most_active_outlet'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-total_complaints_filed']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'most_active_outlet')
