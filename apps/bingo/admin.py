"""Admin configuration for bingo app"""
from django.contrib import admin
from .models import BingoPhrase, BingoCard, BingoSquare


@admin.register(BingoPhrase)
class BingoPhraseAdmin(admin.ModelAdmin):
    """Bingo phrase admin"""
    list_display = ['phrase_text', 'difficulty_level', 'category', 'created_at']
    list_filter = ['difficulty_level', 'category']
    search_fields = ['phrase_text', 'description']
    ordering = ['difficulty_level', 'phrase_text']


class BingoSquareInline(admin.TabularInline):
    """Inline admin for bingo squares"""
    model = BingoSquare
    extra = 0
    readonly_fields = ['position', 'phrase', 'marked', 'marked_at']
    can_delete = False


@admin.register(BingoCard)
class BingoCardAdmin(admin.ModelAdmin):
    """Bingo card admin"""
    list_display = ['id', 'user', 'difficulty', 'completed', 'marked_count', 'completion_time', 'generated_at']
    list_filter = ['difficulty', 'completed', 'generated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'difficulty', 'generated_at', 'completion_time']
    inlines = [BingoSquareInline]

    def marked_count(self, obj):
        return f"{obj.marked_count}/{obj.total_squares}"
    marked_count.short_description = 'Progress'


@admin.register(BingoSquare)
class BingoSquareAdmin(admin.ModelAdmin):
    """Bingo square admin"""
    list_display = ['id', 'card', 'phrase', 'position', 'marked', 'marked_at']
    list_filter = ['marked', 'auto_detected']
    search_fields = ['phrase__phrase_text', 'card__user__username']
    readonly_fields = ['card', 'phrase', 'position']
