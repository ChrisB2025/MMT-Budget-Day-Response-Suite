"""Admin configuration for media complaints"""
from django.contrib import admin
from django.utils import timezone
from .models import MediaOutlet, Complaint, ComplaintLetter, ComplaintStats, OutletSuggestion


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


@admin.register(OutletSuggestion)
class OutletSuggestionAdmin(admin.ModelAdmin):
    """Admin for outlet suggestions"""
    list_display = [
        'id',
        'name',
        'media_type',
        'user',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'media_type', 'created_at']
    search_fields = ['name', 'description', 'user__display_name']
    readonly_fields = ['created_at', 'reviewed_at', 'research_notes']
    ordering = ['-created_at']

    fieldsets = (
        ('Suggestion Details', {
            'fields': ('user', 'name', 'media_type', 'website', 'description', 'status')
        }),
        ('AI Research Results', {
            'fields': (
                'suggested_contact_email',
                'suggested_complaints_email',
                'suggested_regulator',
                'research_notes'
            )
        }),
        ('Admin Review', {
            'fields': ('admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_suggestions', 'reject_suggestions', 'create_outlets_from_suggestions']

    def approve_suggestions(self, request, queryset):
        """Approve selected suggestions"""
        queryset.update(status='approved', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} suggestions approved.")
    approve_suggestions.short_description = "Approve selected suggestions"

    def reject_suggestions(self, request, queryset):
        """Reject selected suggestions"""
        queryset.update(status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} suggestions rejected.")
    reject_suggestions.short_description = "Reject selected suggestions"

    def create_outlets_from_suggestions(self, request, queryset):
        """Create media outlets from approved suggestions"""
        created_count = 0
        for suggestion in queryset.filter(status='approved'):
            MediaOutlet.objects.create(
                name=suggestion.name,
                media_type=suggestion.media_type,
                contact_email=suggestion.suggested_contact_email or '',
                complaints_dept_email=suggestion.suggested_complaints_email or '',
                website=suggestion.website,
                regulator=suggestion.suggested_regulator,
                description=suggestion.description,
                is_active=True
            )
            suggestion.status = 'created'
            suggestion.save()
            created_count += 1

        self.message_user(request, f"{created_count} outlets created from suggestions.")
    create_outlets_from_suggestions.short_description = "Create outlets from approved suggestions"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'reviewed_by')
