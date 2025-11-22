"""Bingo views"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db import models
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import BingoCard, BingoSquare
from .services import generate_bingo_card, mark_square, get_leaderboard


@login_required
def bingo_home(request):
    """Bingo home page"""
    user_cards = BingoCard.objects.filter(user=request.user).order_by('-generated_at')[:5]
    return render(request, 'bingo/home.html', {
        'user_cards': user_cards
    })


@login_required
def generate_card(request):
    """Generate a new bingo card"""
    if request.method == 'POST':
        difficulty = request.POST.get('difficulty', 'classic')

        try:
            card = generate_bingo_card(request.user, difficulty)
            messages.success(request, f'New {difficulty} bingo card generated!')
            return redirect('bingo:card_detail', card_id=card.id)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('bingo:home')

    return render(request, 'bingo/generate.html')


@login_required
def card_detail(request, card_id):
    """View a specific bingo card"""
    card = get_object_or_404(BingoCard, id=card_id, user=request.user)
    squares = card.squares.select_related('phrase').all()

    # Organize squares into 5x5 grid
    grid = [[None for _ in range(5)] for _ in range(5)]
    for square in squares:
        row = square.position // 5
        col = square.position % 5
        grid[row][col] = square

    return render(request, 'bingo/card_detail.html', {
        'card': card,
        'grid': grid
    })


@login_required
def mark_square_view(request, square_id):
    """Mark a bingo square (HTMX endpoint)"""
    if request.method != 'POST':
        return HttpResponse(status=405)

    result = mark_square(square_id, request.user)

    if 'error' in result:
        return HttpResponse(result['error'], status=403)

    square = result['square']

    # Broadcast to WebSocket if marked
    if result['marked']:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'bingo_updates',
            {
                'type': 'square_marked',
                'square_id': square.id,
                'user_id': request.user.id,
                'username': request.user.display_name,
                'timestamp': square.marked_at.isoformat()
            }
        )

        # If completed, broadcast that too
        if result['completed']:
            async_to_sync(channel_layer.group_send)(
                'bingo_updates',
                {
                    'type': 'bingo_completed',
                    'user_id': request.user.id,
                    'username': request.user.display_name,
                    'card_id': square.card.id,
                    'timestamp': square.card.completion_time.isoformat()
                }
            )

    # Return updated square HTML for HTMX swap
    return render(request, 'bingo/partials/square.html', {
        'square': square,
        'card': square.card
    })


def leaderboard_view(request):
    """Bingo leaderboard"""
    leaders = get_leaderboard(limit=50)

    # Check if HTMX request (partial update)
    if request.headers.get('HX-Request'):
        return render(request, 'bingo/partials/leaderboard_table.html', {
            'leaders': leaders
        })

    return render(request, 'bingo/leaderboard.html', {
        'leaders': leaders
    })


def stats_view(request):
    """Bingo statistics"""
    total_cards = BingoCard.objects.count()
    completed_cards = BingoCard.objects.filter(completed=True).count()
    total_players = BingoCard.objects.values('user').distinct().count()

    # Most marked phrases
    most_marked = BingoSquare.objects.filter(marked=True).values(
        'phrase__phrase_text'
    ).annotate(
        count=models.Count('id')
    ).order_by('-count')[:10]

    return render(request, 'bingo/stats.html', {
        'total_cards': total_cards,
        'completed_cards': completed_cards,
        'total_players': total_players,
        'most_marked': most_marked
    })
