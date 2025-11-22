"""Admin configuration for rebuttal app"""
from django.contrib import admin
from .models import Rebuttal, RebuttalSection


class RebuttalSectionInline(admin.TabularInline):
    """Inline admin for rebuttal sections"""
    model = RebuttalSection
    extra = 0
    fields = ['title', 'section_order', 'content']


@admin.register(Rebuttal)
class RebuttalAdmin(admin.ModelAdmin):
    """Rebuttal admin"""
    list_display = ['title', 'version', 'published', 'published_at', 'created_at']
    list_filter = ['published', 'created_at']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RebuttalSectionInline]


@admin.register(RebuttalSection)
class RebuttalSectionAdmin(admin.ModelAdmin):
    """Rebuttal section admin"""
    list_display = ['rebuttal', 'title', 'section_order']
    list_filter = ['rebuttal']
    search_fields = ['title', 'content']
    ordering = ['rebuttal', 'section_order']
