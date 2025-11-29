"""Core views"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.http import HttpResponse
from django.utils import timezone
from apps.bingo.models import BingoCard, BingoPhrase
from apps.factcheck.models import FactCheckRequest, FactCheckResponse
from apps.rebuttal.models import Rebuttal
from .models import UserAction


def home(request):
    """Home page - MMT Campaign Suite main landing"""
    from apps.social_critique.models import SocialMediaCritique
    from apps.article_critique.models import ArticleSubmission
    from apps.media_complaints.models import Complaint

    # Get recent critiques for display
    recent_social_critiques = SocialMediaCritique.objects.filter(
        status='completed'
    ).select_related('user').order_by('-created_at')[:5]

    recent_article_critiques = ArticleSubmission.objects.filter(
        status='completed'
    ).select_related('user').order_by('-created_at')[:5]

    # Overall stats
    stats = {
        'total_critiques': SocialMediaCritique.objects.filter(status='completed').count(),
        'total_articles': ArticleSubmission.objects.filter(status='completed').count(),
        'total_complaints': Complaint.objects.count(),
    }

    return render(request, 'core/home.html', {
        'recent_social_critiques': recent_social_critiques,
        'recent_article_critiques': recent_article_critiques,
        'stats': stats,
    })


def campaigns(request):
    """Campaigns dashboard - shows all recent campaign items"""
    from apps.social_critique.models import SocialMediaCritique
    from apps.article_critique.models import ArticleSubmission
    from apps.media_complaints.models import Complaint

    # Get filters
    campaign_tag = request.GET.get('campaign', '')
    platform_filter = request.GET.get('platform', '')

    # Get all unique campaign tags
    social_tags = SocialMediaCritique.objects.exclude(
        campaign_tag=''
    ).values_list('campaign_tag', flat=True).distinct()

    article_tags = ArticleSubmission.objects.exclude(
        campaign_tag=''
    ).values_list('campaign_tag', flat=True).distinct()

    complaint_tags = Complaint.objects.exclude(
        campaign_tag=''
    ).values_list('campaign_tag', flat=True).distinct()

    all_tags = sorted(set(list(social_tags) + list(article_tags) + list(complaint_tags)))

    # Get available platforms from social critiques
    available_platforms = SocialMediaCritique.objects.filter(
        status='completed'
    ).values_list('platform', flat=True).distinct()

    # Platform display mapping
    platform_choices = [
        ('twitter', 'X/Twitter'),
        ('bluesky', 'Bluesky'),
        ('youtube', 'YouTube'),
        ('reddit', 'Reddit'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('mastodon', 'Mastodon'),
        ('other', 'Other'),
    ]
    platforms = [(p, name) for p, name in platform_choices if p in available_platforms]

    # Build querysets
    social_critiques = SocialMediaCritique.objects.filter(
        status='completed'
    ).select_related('user').order_by('-created_at')

    article_critiques = ArticleSubmission.objects.filter(
        status='completed'
    ).select_related('user').order_by('-created_at')

    complaints = Complaint.objects.select_related('user', 'outlet').order_by('-created_at')

    # Apply campaign tag filter if specified
    if campaign_tag:
        social_critiques = social_critiques.filter(campaign_tag=campaign_tag)
        article_critiques = article_critiques.filter(campaign_tag=campaign_tag)
        complaints = complaints.filter(campaign_tag=campaign_tag)

    # Apply platform filter if specified (only affects social critiques display)
    if platform_filter:
        social_critiques = social_critiques.filter(platform=platform_filter)

    # Limit results
    social_critiques = social_critiques[:20]
    article_critiques = article_critiques[:20]
    complaints = complaints[:20]

    # Stats
    stats = {
        'total_social': SocialMediaCritique.objects.filter(status='completed').count(),
        'total_articles': ArticleSubmission.objects.filter(status='completed').count(),
        'total_complaints': Complaint.objects.count(),
    }

    return render(request, 'core/campaigns.html', {
        'social_critiques': social_critiques,
        'article_critiques': article_critiques,
        'complaints': complaints,
        'campaign_tags': all_tags,
        'selected_tag': campaign_tag,
        'platforms': platforms,
        'selected_platform': platform_filter,
        'stats': stats,
    })


@login_required
def dashboard(request):
    """User dashboard"""
    from apps.social_critique.models import SocialMediaCritique
    from apps.article_critique.models import ArticleSubmission
    from apps.media_complaints.models import Complaint

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

    # User's campaign stats
    campaign_stats = {
        'social_critiques': SocialMediaCritique.objects.filter(user=user).count(),
        'article_critiques': ArticleSubmission.objects.filter(user=user).count(),
        'complaints': Complaint.objects.filter(user=user).count(),
    }

    # Recent actions
    recent_actions = UserAction.objects.filter(user=user)[:10]

    # Achievements
    achievements = user.achievements.all()

    # Recent user submissions
    recent_critiques = SocialMediaCritique.objects.filter(
        user=user
    ).order_by('-created_at')[:5]

    recent_articles = ArticleSubmission.objects.filter(
        user=user
    ).order_by('-created_at')[:5]

    return render(request, 'core/dashboard.html', {
        'bingo_stats': bingo_stats,
        'factcheck_stats': factcheck_stats,
        'campaign_stats': campaign_stats,
        'recent_actions': recent_actions,
        'achievements': achievements,
        'recent_critiques': recent_critiques,
        'recent_articles': recent_articles,
    })


def about(request):
    """About page"""
    return render(request, 'core/about.html')


def help_page(request):
    """Help page"""
    return render(request, 'core/help.html')


def fun_page(request):
    """Fun page - games and interactive content"""
    return render(request, 'core/fun.html')


def league_table(request):
    """League table showing social media users who have been critiqued, ranked by various metrics"""
    from apps.social_critique.models import SocialMediaCritique
    from django.db.models import Count, Max, Avg, F, Value, FloatField
    from django.db.models.functions import Coalesce

    # Get sort parameter (default to weighted_score)
    sort_by = request.GET.get('sort', 'weighted_score')
    order = request.GET.get('order', 'desc')
    platform_filter = request.GET.get('platform', '')

    # Valid sort options
    valid_sorts = ['critique_count', 'follower_count', 'latest_critique', 'weighted_score']
    if sort_by not in valid_sorts:
        sort_by = 'weighted_score'

    # Build the queryset - aggregate by source_author
    # Filter to only include critiques with author names
    queryset = SocialMediaCritique.objects.filter(
        status='completed'
    ).exclude(
        source_author=''
    ).exclude(
        source_author__isnull=True
    )

    # Apply platform filter if specified
    if platform_filter:
        queryset = queryset.filter(platform=platform_filter)

    # Aggregate by author
    league_data = queryset.values(
        'source_author',
    ).annotate(
        critique_count=Count('id'),
        follower_count=Max('source_author_follower_count'),  # Use latest known follower count
        latest_critique=Max('created_at'),
        # Get the bio and platform from the latest critique
    ).filter(critique_count__gte=1)

    # Calculate weighted score for each entry
    # Formula: (critique_count * 10) + (log10(follower_count + 1) * 5) + recency_bonus
    # This prioritizes repeat offenders with large audiences
    import math
    from datetime import timedelta

    league_list = []
    for entry in league_data:
        follower_count = entry['follower_count'] or 0
        critique_count = entry['critique_count'] or 0
        latest_critique = entry['latest_critique']

        # Calculate weighted score
        # Base score from critique count (10 points each)
        critique_score = critique_count * 10

        # Follower influence (logarithmic scale to prevent huge accounts from dominating)
        follower_score = math.log10(follower_count + 1) * 5 if follower_count > 0 else 0

        # Recency bonus (more points for recent critiques)
        days_since = (timezone.now() - latest_critique).days if latest_critique else 365
        recency_score = max(0, 30 - days_since)  # Up to 30 bonus points for very recent

        weighted_score = critique_score + follower_score + recency_score

        # Get additional info from the most recent critique for this author
        latest = SocialMediaCritique.objects.filter(
            source_author=entry['source_author'],
            status='completed'
        ).order_by('-created_at').first()

        league_list.append({
            'handle': entry['source_author'],
            'bio': latest.source_author_bio if latest else '',
            'platform': latest.platform if latest else '',
            'platform_display': latest.get_platform_display() if latest else '',
            'critique_count': critique_count,
            'follower_count': follower_count,
            'latest_critique': latest_critique,
            'weighted_score': round(weighted_score, 1),
            'latest_critique_id': latest.share_id if latest else None,
        })

    # Sort the list
    reverse_order = order == 'desc'
    if sort_by == 'latest_critique':
        league_list.sort(key=lambda x: x['latest_critique'] or timezone.now(), reverse=reverse_order)
    elif sort_by == 'follower_count':
        league_list.sort(key=lambda x: x['follower_count'] or 0, reverse=reverse_order)
    elif sort_by == 'critique_count':
        league_list.sort(key=lambda x: x['critique_count'], reverse=reverse_order)
    else:  # weighted_score
        league_list.sort(key=lambda x: x['weighted_score'], reverse=reverse_order)

    # Get available platforms for filter
    available_platforms = SocialMediaCritique.objects.filter(
        status='completed'
    ).exclude(
        source_author=''
    ).values_list('platform', flat=True).distinct()

    platform_choices = [
        ('twitter', 'X/Twitter'),
        ('bluesky', 'Bluesky'),
        ('youtube', 'YouTube'),
        ('reddit', 'Reddit'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('mastodon', 'Mastodon'),
        ('other', 'Other'),
    ]
    platforms = [(p, name) for p, name in platform_choices if p in available_platforms]

    return render(request, 'core/league_table.html', {
        'league_data': league_list[:100],  # Limit to top 100
        'sort_by': sort_by,
        'order': order,
        'platforms': platforms,
        'selected_platform': platform_filter,
        'total_count': len(league_list),
    })


# Redirect for retired fact-check public route
def factcheck_retired(request):
    """Redirect old fact-check URLs to home with a message"""
    messages.info(request, 'The Fact-Check feature has been integrated into our Campaign Tools. Use the homepage to submit content for analysis.')
    return redirect('core:home')


@staff_member_required
def admin_dashboard(request):
    """
    Comprehensive admin dashboard with links to all diagnostic and management tools.
    Only accessible to staff/admin users.
    """
    from apps.social_critique.models import SocialMediaCritique
    from apps.article_critique.models import ArticleSubmission
    from apps.media_complaints.models import Complaint

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
        'campaigns': {
            'social_critiques': SocialMediaCritique.objects.count(),
            'article_critiques': ArticleSubmission.objects.count(),
            'complaints': Complaint.objects.count(),
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




@staff_member_required
def reset_test_data(request):
    """
    Reset test data for v1 launch.
    Clears bingo cards and resets user points.
    Staff-only view.
    """
    from apps.bingo.models import BingoCard
    from apps.users.models import User
    from apps.core.models import UserAction

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'clear_bingo':
            count = BingoCard.objects.all().delete()[0]
            messages.success(request, f'Deleted {count} bingo card(s) and associated squares.')

        elif action == 'reset_points':
            User.objects.all().update(points=0)
            messages.success(request, 'Reset all user points to 0.')

        elif action == 'clear_actions':
            count = UserAction.objects.all().delete()[0]
            messages.success(request, f'Deleted {count} user action(s).')

        elif action == 'clear_all':
            bingo_count = BingoCard.objects.all().delete()[0]
            User.objects.all().update(points=0)
            action_count = UserAction.objects.all().delete()[0]
            messages.success(request, f'Cleared ALL test data: {bingo_count} bingo cards, all points reset, {action_count} actions.')

        return redirect('core:reset_test_data')

    # GET request - show stats
    stats = {
        'bingo_cards': BingoCard.objects.count(),
        'completed_cards': BingoCard.objects.filter(completed=True).count(),
        'total_user_points': User.objects.aggregate(Sum('points'))['points__sum'] or 0,
        'users_with_points': User.objects.filter(points__gt=0).count(),
        'user_actions': UserAction.objects.count(),
    }

    return render(request, 'core/reset_test_data.html', {
        'stats': stats
    })


@staff_member_required
def grant_superuser_access(request):
    """
    Web-accessible endpoint for staff to grant themselves superuser access.
    Requires existing staff status to access.
    """
    from apps.users.models import User

    if request.method == 'POST':
        # Grant superuser to current user
        user = request.user

        if user.is_superuser:
            messages.info(request, f'You already have superuser access!')
        else:
            user.is_superuser = True
            user.save()
            messages.success(request, f'Successfully granted superuser access! You now have full admin access.')
            messages.success(request, 'You can now access the Django Admin panel at /admin/')

        return redirect('core:admin_dashboard')

    # GET request - show confirmation page
    return render(request, 'core/grant_superuser.html', {
        'user': request.user,
        'is_superuser': request.user.is_superuser,
    })


def health_check(request):
    """
    Health check endpoint for deployment diagnostics.
    Returns JSON with system status and any errors.
    """
    import json
    from django.db import connection
    from django.conf import settings

    status = {
        'status': 'ok',
        'checks': {},
        'errors': []
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        status['checks']['database'] = 'connected'
    except Exception as e:
        status['checks']['database'] = 'error'
        status['errors'].append(f'Database: {str(e)}')
        status['status'] = 'error'

    # Check if tables exist
    try:
        from apps.social_critique.models import SocialMediaCritique
        from apps.article_critique.models import ArticleSubmission
        from apps.media_complaints.models import Complaint, MediaOutlet
        from apps.bingo.models import BingoPhrase

        table_checks = {
            'social_critiques': SocialMediaCritique.objects.count(),
            'article_submissions': ArticleSubmission.objects.count(),
            'complaints': Complaint.objects.count(),
            'media_outlets': MediaOutlet.objects.count(),
            'bingo_phrases': BingoPhrase.objects.count(),
        }
        status['checks']['tables'] = table_checks
    except Exception as e:
        status['checks']['tables'] = 'error'
        status['errors'].append(f'Tables: {str(e)}')
        status['status'] = 'error'

    # Check Redis connection
    try:
        import redis
        redis_url = getattr(settings, 'REDIS_URL', None)
        if redis_url:
            r = redis.from_url(redis_url)
            r.ping()
            status['checks']['redis'] = 'connected'
        else:
            status['checks']['redis'] = 'not configured'
    except Exception as e:
        status['checks']['redis'] = 'error'
        status['errors'].append(f'Redis: {str(e)}')
        # Redis error is not critical for basic functionality

    # Check channel layer configuration
    try:
        channel_layers = getattr(settings, 'CHANNEL_LAYERS', {})
        default_layer = channel_layers.get('default', {})
        backend = default_layer.get('BACKEND', 'unknown')
        if 'InMemoryChannelLayer' in backend:
            status['checks']['channel_layer'] = 'in_memory (fallback)'
        elif 'RedisChannelLayer' in backend:
            status['checks']['channel_layer'] = 'redis'
        else:
            status['checks']['channel_layer'] = backend
    except Exception as e:
        status['checks']['channel_layer'] = 'error'
        status['errors'].append(f'Channel layer: {str(e)}')

    # Environment check
    status['checks']['env'] = {
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'database_configured': bool(settings.DATABASES.get('default', {}).get('NAME')),
        'anthropic_key_set': bool(getattr(settings, 'ANTHROPIC_API_KEY', '')),
    }

    response_status = 200 if status['status'] == 'ok' else 500
    return HttpResponse(
        json.dumps(status, indent=2, default=str),
        content_type='application/json',
        status=response_status
    )
