"""Core views"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from apps.bingo.models import BingoCard
from apps.factcheck.models import FactCheckRequest
from .models import UserAction


def home(request):
    """Home page"""
    # Overall stats
    total_bingo_cards = BingoCard.objects.count()
    total_factchecks = FactCheckRequest.objects.count()

    return render(request, 'core/home.html', {
        'total_bingo_cards': total_bingo_cards,
        'total_factchecks': total_factchecks,
    })


@login_required
def dashboard(request):
    """User dashboard"""
    user = request.user

    # User's bingo stats
    user_bingo_cards = BingoCard.objects.filter(user=user)
    bingo_stats = {
        'total_cards': user_bingo_cards.count(),
        'completed_cards': user_bingo_cards.filter(completed=True).count(),
        'latest_card': user_bingo_cards.first()
    }

    # User's fact-check stats
    user_factchecks = FactCheckRequest.objects.filter(user=user)
    factcheck_stats = {
        'total_submitted': user_factchecks.count(),
        'total_answered': user_factchecks.filter(status__in=['reviewed', 'published']).count(),
    }

    # Recent actions
    recent_actions = UserAction.objects.filter(user=user)[:10]

    # Achievements
    achievements = user.achievements.all()

    return render(request, 'core/dashboard.html', {
        'bingo_stats': bingo_stats,
        'factcheck_stats': factcheck_stats,
        'recent_actions': recent_actions,
        'achievements': achievements,
    })


def about(request):
    """About page"""
    return render(request, 'core/about.html')


def help_page(request):
    """Help page"""
    return render(request, 'core/help.html')
