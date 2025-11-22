"""Rebuttal models"""
from django.db import models


class Rebuttal(models.Model):
    """Comprehensive rebuttal document"""
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=10, default='1.0')
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rebuttals'
        verbose_name = 'Rebuttal'
        verbose_name_plural = 'Rebuttals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['version']),
            models.Index(fields=['published']),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version})"


class RebuttalSection(models.Model):
    """Section within a rebuttal document"""
    rebuttal = models.ForeignKey(
        Rebuttal,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    section_order = models.IntegerField()

    class Meta:
        db_table = 'rebuttal_sections'
        verbose_name = 'Rebuttal Section'
        verbose_name_plural = 'Rebuttal Sections'
        ordering = ['section_order']

    def __str__(self):
        return f"{self.rebuttal.title} - {self.title}"
