"""Bingo business logic"""
import random
from django.utils import timezone
from .models import BingoCard, BingoSquare, BingoPhrase


def generate_bingo_card(user, difficulty='classic'):
    """
    Generate a new bingo card for a user.

    Args:
        user: User instance
        difficulty: 'classic', 'advanced', or 'technical'

    Returns:
        BingoCard instance
    """
    # Get available phrases for difficulty level
    phrases = list(BingoPhrase.objects.filter(difficulty_level=difficulty))

    if len(phrases) < 25:
        raise ValueError(f"Not enough phrases for {difficulty} difficulty. Need at least 25.")

    # Randomly select 25 unique phrases
    selected_phrases = random.sample(phrases, 25)

    # Create card
    card = BingoCard.objects.create(
        user=user,
        difficulty=difficulty
    )

    # Create squares
    for position, phrase in enumerate(selected_phrases):
        square = BingoSquare.objects.create(
            card=card,
            phrase=phrase,
            position=position
        )

        # Mark center square (position 12) as free space
        if position == 12:
            square.marked = True
            square.marked_at = timezone.now()
            square.auto_detected = True
            square.save()

    return card


def check_bingo_completion(card):
    """
    Check if a bingo card has bingo (5 in a row).

    Checks:
    - All rows
    - All columns
    - Both diagonals

    Args:
        card: BingoCard instance

    Returns:
        bool: True if bingo is achieved
    """
    squares = card.squares.all()
    grid = {}
    for square in squares:
        grid[square.position] = square.marked

    # Check rows
    for row in range(5):
        if all(grid.get(row * 5 + col, False) for col in range(5)):
            return True

    # Check columns
    for col in range(5):
        if all(grid.get(row * 5 + col, False) for row in range(5)):
            return True

    # Check diagonal (top-left to bottom-right)
    if all(grid.get(i * 5 + i, False) for i in range(5)):
        return True

    # Check diagonal (top-right to bottom-left)
    if all(grid.get(i * 5 + (4 - i), False) for i in range(5)):
        return True

    return False


def get_leaderboard(limit=50):
    """
    Get bingo leaderboard of fastest completions.

    Args:
        limit: Maximum number of entries

    Returns:
        QuerySet of BingoCard instances
    """
    return BingoCard.objects.filter(
        completed=True
    ).select_related('user').order_by('completion_time')[:limit]


def mark_square(square_id, user):
    """
    Mark a bingo square and check for completion.

    Args:
        square_id: BingoSquare ID
        user: User instance

    Returns:
        dict with 'marked', 'completed', 'square'
    """
    try:
        square = BingoSquare.objects.select_related('card').get(
            id=square_id,
            card__user=user
        )
    except BingoSquare.DoesNotExist:
        return {'error': 'Square not found or access denied'}

    if square.marked:
        return {
            'marked': False,
            'completed': False,
            'square': square,
            'already_marked': True
        }

    # Mark the square
    square.marked = True
    square.marked_at = timezone.now()
    square.save()

    # Check for completion
    card = square.card
    is_complete = check_bingo_completion(card)

    if is_complete and not card.completed:
        card.completed = True
        card.completion_time = timezone.now()
        card.save()

        # Update user points
        user.points += 100  # Award points for completion
        user.save()

    return {
        'marked': True,
        'completed': is_complete,
        'square': square,
        'already_marked': False
    }
