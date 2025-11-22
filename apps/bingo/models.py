"""Bingo models"""
from django.db import models
from django.conf import settings


class BingoPhrase(models.Model):
    """Library of bingo phrases/myths"""
    DIFFICULTY_CHOICES = [
        ('classic', 'Classic'),
        ('advanced', 'Advanced'),
        ('technical', 'Technical'),
    ]

    phrase_text = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    description = models.TextField(blank=True, help_text='Explanation of why this is a myth')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bingo_phrases'
        verbose_name = 'Bingo Phrase'
        verbose_name_plural = 'Bingo Phrases'
        indexes = [
            models.Index(fields=['difficulty_level']),
        ]

    def __str__(self):
        return f"{self.phrase_text} ({self.difficulty_level})"


class BingoCard(models.Model):
    """Generated bingo card for a user"""
    DIFFICULTY_CHOICES = BingoPhrase.DIFFICULTY_CHOICES

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bingo_cards'
    )
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    completed = models.BooleanField(default=False)
    completion_time = models.DateTimeField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bingo_cards'
        verbose_name = 'Bingo Card'
        verbose_name_plural = 'Bingo Cards'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['completed']),
        ]

    def __str__(self):
        return f"Card #{self.id} - {self.user.display_name} ({self.difficulty})"

    @property
    def marked_count(self):
        """Count of marked squares"""
        return self.squares.filter(marked=True).count()

    @property
    def total_squares(self):
        """Total number of squares"""
        return self.squares.count()


class BingoSquare(models.Model):
    """Individual square on a bingo card"""
    card = models.ForeignKey(
        BingoCard,
        on_delete=models.CASCADE,
        related_name='squares'
    )
    phrase = models.ForeignKey(
        BingoPhrase,
        on_delete=models.CASCADE
    )
    position = models.IntegerField(help_text='Position 0-24 in 5x5 grid')
    marked = models.BooleanField(default=False)
    marked_at = models.DateTimeField(null=True, blank=True)
    auto_detected = models.BooleanField(default=False)

    class Meta:
        db_table = 'bingo_squares'
        verbose_name = 'Bingo Square'
        verbose_name_plural = 'Bingo Squares'
        unique_together = [['card', 'position']]
        ordering = ['position']
        indexes = [
            models.Index(fields=['card']),
            models.Index(fields=['marked']),
        ]

    def __str__(self):
        return f"Square {self.position}: {self.phrase.phrase_text}"

    @property
    def row(self):
        """Get row number (0-4)"""
        return self.position // 5

    @property
    def col(self):
        """Get column number (0-4)"""
        return self.position % 5
