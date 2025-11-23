"""Fact-check views"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import models
from django.db.models import Q
from django.utils import timezone
from .models import (
    FactCheckRequest, FactCheckUpvote, UserProfile, UserBadge,
    UserFollow, ClaimComment, ClaimOfTheDay
)
from .forms import FactCheckSubmitForm
from .tasks import process_fact_check
from .services import (
    get_or_create_user_profile, check_and_award_badges,
    update_hot_streak, award_experience_points, get_live_feed,
    get_leaderboard, get_claim_stats
)


def factcheck_home(request):
    """Fact-check home page with competition features"""
    # Get basic requests (most likely to work)
    recent_requests = []
    try:
        recent_requests = FactCheckRequest.objects.filter(
            status__in=['reviewed', 'published']
        ).select_related('user').order_by('-created_at')[:10]
    except Exception:
        # Even more basic fallback
        try:
            recent_requests = FactCheckRequest.objects.select_related('user').order_by('-created_at')[:10]
        except Exception:
            pass

    # Get claim of the day (gracefully handle if table doesn't exist)
    claim_of_day = None
    try:
        today = timezone.now().date()
        claim_of_day = ClaimOfTheDay.objects.filter(
            featured_date=today
        ).select_related('request__user').first()
    except Exception:
        pass

    # Get live feed (gracefully handle if new tables don't exist)
    live_feed = []
    try:
        live_feed = get_live_feed(limit=10)
    except Exception:
        # If new tables don't exist, just show recent requests
        try:
            live_feed = FactCheckRequest.objects.select_related('user').order_by('-created_at')[:10]
        except Exception:
            pass

    # Get leaderboard (may be empty if profiles don't exist yet)
    leaderboard = []
    try:
        leaderboard = get_leaderboard('all')
    except Exception:
        pass

    # Get stats (with safe defaults)
    stats = {'total_claims': 0, 'claims_today': 0, 'high_severity_count': 0}
    try:
        stats = get_claim_stats()
    except Exception:
        # Try basic count at least
        try:
            stats['total_claims'] = FactCheckRequest.objects.count()
        except Exception:
            pass

    # Get user profile if authenticated
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = get_or_create_user_profile(request.user)
        except Exception:
            pass

    return render(request, 'factcheck/home.html', {
        'recent_requests': recent_requests,
        'claim_of_day': claim_of_day,
        'live_feed': live_feed,
        'leaderboard': leaderboard,
        'stats': stats,
        'user_profile': user_profile,
    })


@login_required
def submit_factcheck(request):
    """Submit a new fact-check request"""
    # Get or create user profile for stats display
    user_profile = None
    try:
        user_profile = get_or_create_user_profile(request.user)
    except Exception:
        # Profile tables may not exist yet (migrations not run)
        pass

    if request.method == 'POST':
        form = FactCheckSubmitForm(request.POST)
        if form.is_valid():
            fact_check = form.save(commit=False)
            fact_check.user = request.user
            fact_check.save()

            # Try to award experience points and badges (gracefully handle if tables don't exist)
            streak = 1
            badges_awarded = []
            try:
                award_experience_points(request.user, 10)  # 10 XP per submission
                streak = update_hot_streak(request.user)
                badges_awarded = check_and_award_badges(request.user)
            except Exception:
                # Tables don't exist yet, skip gamification
                pass

            # Build success message
            success_msg = 'Fact-check request submitted!'
            if user_profile:
                success_msg += ' +10 XP'
                if streak > 1:
                    success_msg += f' 🔥 Hot Streak: {streak}!'
                if badges_awarded:
                    success_msg += f' 🏆 New badge(s) earned!'

            # Trigger processing (try async first, fallback to sync)
            processing_started = False
            try:
                # Try Celery async processing
                process_fact_check.delay(fact_check.id)
                processing_started = True
                messages.success(request, success_msg + ' AI is generating a response...')
            except Exception as e:
                # Celery not available - process synchronously RIGHT NOW
                try:
                    from .services import process_fact_check_request
                    result = process_fact_check_request(fact_check.id)

                    if result['status'] == 'success':
                        processing_started = True
                        messages.success(request, success_msg + ' ✅ Fact-check complete!')
                    else:
                        messages.warning(
                            request,
                            success_msg + f' ⚠️ Processing failed: {result.get("message", "Unknown error")}'
                        )
                except Exception as sync_error:
                    messages.error(
                        request,
                        success_msg + f' ❌ Error: {str(sync_error)}'
                    )

            # For HTMX requests, return partial with animations
            if request.headers.get('HX-Request'):
                return render(request, 'factcheck/partials/request_card.html', {
                    'request': fact_check,
                    'new_submission': True,
                    'badges_awarded': badges_awarded,
                    'streak': streak,
                })

            return redirect('factcheck:detail', request_id=fact_check.id)
    else:
        form = FactCheckSubmitForm()

    return render(request, 'factcheck/submit.html', {
        'form': form,
        'user_profile': user_profile
    })


def factcheck_queue(request):
    """View queue of fact-check requests"""
    status_filter = request.GET.get('status', 'all')

    requests = FactCheckRequest.objects.select_related('user', 'response')

    if status_filter != 'all':
        requests = requests.filter(status=status_filter)

    requests = requests.order_by('-upvotes', '-created_at')

    # For HTMX pagination
    if request.headers.get('HX-Request'):
        return render(request, 'factcheck/partials/queue_list.html', {
            'requests': requests
        })

    return render(request, 'factcheck/queue.html', {
        'requests': requests,
        'status_filter': status_filter
    })


def factcheck_detail(request, request_id):
    """View a specific fact-check request and response"""
    fact_check = get_object_or_404(
        FactCheckRequest.objects.select_related('user', 'response'),
        id=request_id
    )

    has_upvoted = False
    if request.user.is_authenticated:
        has_upvoted = FactCheckUpvote.objects.filter(
            user=request.user,
            request=fact_check
        ).exists()

    return render(request, 'factcheck/detail.html', {
        'request': fact_check,
        'has_upvoted': has_upvoted
    })


@login_required
def upvote_factcheck(request, request_id):
    """Upvote a fact-check request"""
    if request.method != 'POST':
        return HttpResponse(status=405)

    fact_check = get_object_or_404(FactCheckRequest, id=request_id)

    # Toggle upvote
    upvote, created = FactCheckUpvote.objects.get_or_create(
        user=request.user,
        request=fact_check
    )

    if not created:
        # User already upvoted, remove it
        upvote.delete()
        fact_check.upvotes -= 1
        fact_check.save()
        has_upvoted = False
    else:
        # New upvote
        fact_check.upvotes += 1
        fact_check.save()
        has_upvoted = True

    # Return updated upvote button for HTMX
    return render(request, 'factcheck/partials/upvote_button.html', {
        'request': fact_check,
        'has_upvoted': has_upvoted
    })


def factcheck_stats(request):
    """Fact-check statistics"""
    total_submitted = FactCheckRequest.objects.count()
    total_answered = FactCheckRequest.objects.filter(
        status__in=['reviewed', 'published']
    ).count()

    avg_severity = FactCheckRequest.objects.aggregate(
        models.Avg('severity')
    )['severity__avg'] or 0

    top_contributors = FactCheckRequest.objects.values(
        'user__display_name'
    ).annotate(
        count=models.Count('id')
    ).order_by('-count')[:10]

    return render(request, 'factcheck/stats.html', {
        'total_submitted': total_submitted,
        'total_answered': total_answered,
        'avg_severity': round(avg_severity, 1),
        'top_contributors': top_contributors
    })


@login_required
def user_dashboard(request):
    """Personal dashboard for fact-checkers"""
    profile = get_or_create_user_profile(request.user)
    profile.update_stats()

    # Get user's recent claims
    recent_claims = FactCheckRequest.objects.filter(
        user=request.user
    ).select_related('response').order_by('-created_at')[:10]

    # Get user's badges
    badges = UserBadge.objects.filter(user=request.user).order_by('-earned_at')

    # Calculate success rate
    total_claims = profile.total_claims_submitted
    fact_checked_claims = profile.claims_fact_checked
    success_rate = (fact_checked_claims / total_claims * 100) if total_claims > 0 else 0

    # Progress to next level
    current_xp = profile.experience_points
    if profile.level == 'bronze':
        next_level_xp = 200
    elif profile.level == 'silver':
        next_level_xp = 500
    elif profile.level == 'gold':
        next_level_xp = 1000
    else:
        next_level_xp = current_xp  # Already at max level

    progress_percentage = (current_xp / next_level_xp * 100) if next_level_xp > 0 else 100

    return render(request, 'factcheck/dashboard.html', {
        'profile': profile,
        'recent_claims': recent_claims,
        'badges': badges,
        'success_rate': round(success_rate, 1),
        'progress_percentage': min(progress_percentage, 100),
        'next_level_xp': next_level_xp,
    })


@login_required
def user_profile(request, user_id):
    """View another user's profile"""
    from apps.users.models import User
    profile_user = get_object_or_404(User, id=user_id)
    profile = get_or_create_user_profile(profile_user)

    # Check if current user is following this user
    is_following = False
    if request.user.is_authenticated:
        is_following = UserFollow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    # Get user's recent claims
    recent_claims = FactCheckRequest.objects.filter(
        user=profile_user
    ).order_by('-created_at')[:10]

    # Get badges
    badges = UserBadge.objects.filter(user=profile_user).order_by('-earned_at')

    return render(request, 'factcheck/user_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'recent_claims': recent_claims,
        'badges': badges,
        'is_following': is_following,
    })


@login_required
def follow_user(request, user_id):
    """Follow/unfollow a user"""
    if request.method != 'POST':
        return HttpResponse(status=405)

    from apps.users.models import User
    user_to_follow = get_object_or_404(User, id=user_id)

    if user_to_follow == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    # Toggle follow
    follow, created = UserFollow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )

    if not created:
        # Already following, unfollow
        follow.delete()
        is_following = False
    else:
        is_following = True

    return JsonResponse({
        'is_following': is_following,
        'follower_count': user_to_follow.factcheck_followers.count()
    })


@login_required
def add_comment(request, request_id):
    """Add a comment to a claim"""
    if request.method != 'POST':
        return HttpResponse(status=405)

    fact_check = get_object_or_404(FactCheckRequest, id=request_id)
    comment_text = request.POST.get('comment_text', '').strip()

    if not comment_text:
        return JsonResponse({'error': 'Comment cannot be empty'}, status=400)

    comment = ClaimComment.objects.create(
        request=fact_check,
        user=request.user,
        text=comment_text
    )

    # For HTMX requests, return the comment partial
    if request.headers.get('HX-Request'):
        return render(request, 'factcheck/partials/comment.html', {
            'comment': comment
        })

    return JsonResponse({
        'id': comment.id,
        'user': comment.user.display_name,
        'text': comment.text,
        'created_at': comment.created_at.isoformat()
    })


def leaderboard(request):
    """View leaderboard"""
    timeframe = request.GET.get('timeframe', 'all')
    top_users = get_leaderboard(timeframe)

    return render(request, 'factcheck/leaderboard.html', {
        'top_users': top_users,
        'timeframe': timeframe,
    })


def live_feed_view(request):
    """Live feed of recent claims"""
    feed = get_live_feed(limit=30)

    return render(request, 'factcheck/live_feed.html', {
        'feed': feed,
    })


@login_required
def share_to_twitter(request, request_id):
    """Generate Twitter share link for a claim"""
    fact_check = get_object_or_404(FactCheckRequest, id=request_id)

    # Build share text
    share_text = f"🔍 Fact-check needed: {fact_check.claim_text[:100]}..."
    if fact_check.severity >= 8:
        share_text = f"🚨 HIGH PRIORITY " + share_text

    # Build full URL
    claim_url = request.build_absolute_uri(f'/factcheck/{fact_check.id}/')

    # Twitter share URL
    twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={claim_url}&hashtags=FactCheck,MMT,BudgetDay"

    return JsonResponse({'twitter_url': twitter_url})


@login_required
def diagnostics(request):
    """Web-accessible diagnostics page for fact-check configuration"""
    from django.conf import settings
    from celery import current_app
    import redis

    # Only allow staff users
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can access diagnostics')
        return redirect('factcheck:home')

    results = {
        'api_key': {'status': 'unknown', 'message': '', 'details': ''},
        'redis': {'status': 'unknown', 'message': '', 'details': ''},
        'celery': {'status': 'unknown', 'message': '', 'details': '', 'tasks': []},
        'claims': {'submitted': 0, 'processing': 0, 'reviewed': 0},
        'api_test': {'status': 'unknown', 'message': '', 'details': ''},
    }

    # 1. Check Anthropic API Key
    try:
        if settings.ANTHROPIC_API_KEY:
            key_preview = settings.ANTHROPIC_API_KEY[:15] + '...' if len(settings.ANTHROPIC_API_KEY) > 15 else settings.ANTHROPIC_API_KEY
            results['api_key']['status'] = 'success'
            results['api_key']['message'] = f'API Key configured: {key_preview}'
        else:
            results['api_key']['status'] = 'error'
            results['api_key']['message'] = 'ANTHROPIC_API_KEY is NOT set!'
            results['api_key']['details'] = 'Set ANTHROPIC_API_KEY in your environment variables'
    except Exception as e:
        results['api_key']['status'] = 'error'
        results['api_key']['message'] = f'Error checking API key: {str(e)}'

    # 2. Check Redis Connection
    try:
        results['redis']['details'] = f'Broker URL: {settings.CELERY_BROKER_URL}'
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        results['redis']['status'] = 'success'
        results['redis']['message'] = 'Redis connection successful'
    except Exception as e:
        results['redis']['status'] = 'error'
        results['redis']['message'] = f'Redis connection failed: {str(e)}'
        results['redis']['details'] = 'Check REDIS_URL and CELERY_BROKER_URL settings'

    # 3. Check Celery Configuration
    try:
        results['celery']['details'] = f'Broker: {current_app.conf.broker_url}, Backend: {current_app.conf.result_backend}'

        # Check if tasks are registered
        registered_tasks = list(current_app.tasks.keys())
        fact_check_tasks = [t for t in registered_tasks if 'fact' in t.lower()]

        if fact_check_tasks:
            results['celery']['status'] = 'success'
            results['celery']['message'] = f'Found {len(fact_check_tasks)} fact-check task(s)'
            results['celery']['tasks'] = fact_check_tasks
        else:
            results['celery']['status'] = 'warning'
            results['celery']['message'] = 'No fact-check tasks found in registry'
    except Exception as e:
        results['celery']['status'] = 'error'
        results['celery']['message'] = f'Celery check failed: {str(e)}'

    # 4. Check pending claims
    try:
        results['claims']['submitted'] = FactCheckRequest.objects.filter(status='submitted').count()
        results['claims']['processing'] = FactCheckRequest.objects.filter(status='processing').count()
        results['claims']['reviewed'] = FactCheckRequest.objects.filter(status='reviewed').count()
    except Exception as e:
        results['claims']['error'] = str(e)

    # 5. Try a test API call
    if settings.ANTHROPIC_API_KEY:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=50,
                messages=[{"role": "user", "content": "Say 'test successful'"}]
            )

            results['api_test']['status'] = 'success'
            results['api_test']['message'] = 'Claude API test successful'
            results['api_test']['details'] = f'Response: {response.content[0].text}'
        except Exception as e:
            results['api_test']['status'] = 'error'
            results['api_test']['message'] = f'Claude API test failed: {str(e)}'
    else:
        results['api_test']['status'] = 'error'
        results['api_test']['message'] = 'Skipped (no API key)'

    return render(request, 'factcheck/diagnostics.html', {
        'results': results
    })


@login_required
def process_stuck_claims(request):
    """Web-accessible page to process stuck fact-check claims"""
    from .services import process_fact_check_request

    # Only allow staff users
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can process stuck claims')
        return redirect('factcheck:home')

    # Get stuck requests
    stuck_requests = FactCheckRequest.objects.filter(
        Q(status='submitted') | Q(status='processing')
    ).order_by('created_at')

    total = stuck_requests.count()

    # If POST request, process them
    if request.method == 'POST':
        limit = request.POST.get('limit', None)
        if limit:
            stuck_requests = stuck_requests[:int(limit)]

        success_count = 0
        error_count = 0
        results = []

        for req in stuck_requests:
            result = {
                'id': req.id,
                'claim': req.claim_text[:50] + '...' if len(req.claim_text) > 50 else req.claim_text,
                'status': 'unknown',
                'message': ''
            }

            try:
                process_result = process_fact_check_request(req.id)

                if process_result['status'] == 'success':
                    success_count += 1
                    result['status'] = 'success'
                    result['message'] = f'Success! Response ID: {process_result["response_id"]}'
                else:
                    error_count += 1
                    result['status'] = 'error'
                    result['message'] = process_result.get('message', 'Unknown error')
            except Exception as e:
                error_count += 1
                result['status'] = 'error'
                result['message'] = str(e)

            results.append(result)

        messages.success(request, f'Processed {success_count} successfully. Failed: {error_count}')

        return render(request, 'factcheck/process_stuck.html', {
            'total': total,
            'results': results,
            'processed': True
        })

    # GET request - just show what's stuck
    return render(request, 'factcheck/process_stuck.html', {
        'total': total,
        'stuck_requests': stuck_requests,
        'processed': False
    })
