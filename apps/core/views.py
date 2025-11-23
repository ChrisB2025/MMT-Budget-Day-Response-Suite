"""Core views"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.http import HttpResponse
from apps.bingo.models import BingoCard, BingoPhrase
from apps.factcheck.models import FactCheckRequest, FactCheckResponse
from apps.rebuttal.models import Rebuttal
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


@staff_member_required
def admin_dashboard(request):
    """
    Comprehensive admin dashboard with links to all diagnostic and management tools.
    Only accessible to staff/admin users.
    """
    # Collect system statistics
    stats = {
        'factcheck': {
            'total': FactCheckRequest.objects.count(),
            'submitted': FactCheckRequest.objects.filter(status='submitted').count(),
            'processing': FactCheckRequest.objects.filter(status='processing').count(),
            'reviewed': FactCheckRequest.objects.filter(status='reviewed').count(),
            'published': FactCheckRequest.objects.filter(status='published').count(),
        },
        'bingo': {
            'total_cards': BingoCard.objects.count(),
            'completed_cards': BingoCard.objects.filter(completed=True).count(),
            'total_phrases': BingoPhrase.objects.count(),
            'total_players': BingoCard.objects.values('user').distinct().count(),
        },
        'rebuttal': {
            'total': Rebuttal.objects.count(),
            'published': Rebuttal.objects.filter(published=True).count(),
        },
        'users': {
            'total': request.user.__class__.objects.count(),
            'staff': request.user.__class__.objects.filter(is_staff=True).count(),
            'superusers': request.user.__class__.objects.filter(is_superuser=True).count(),
        }
    }

    return render(request, 'core/admin_dashboard.html', {
        'stats': stats
    })


@staff_member_required
def delete_test_submissions(request):
    """
    Delete test fact-check submissions.
    Staff-only view for cleaning up test data.
    """
    if request.method == 'POST':
        # Get IDs to delete
        delete_ids = request.POST.getlist('delete_ids')

        if delete_ids:
            # Delete the selected fact-check requests (responses will cascade)
            deleted_count = FactCheckRequest.objects.filter(id__in=delete_ids).delete()[0]
            messages.success(request, f'Successfully deleted {deleted_count} fact-check submission(s)')
        else:
            messages.warning(request, 'No submissions selected for deletion')

        return redirect('core:delete_test_submissions')

    # GET request - show all submissions
    all_submissions = FactCheckRequest.objects.select_related('user', 'response').order_by('-created_at')

    return render(request, 'core/delete_test_submissions.html', {
        'submissions': all_submissions
    })
