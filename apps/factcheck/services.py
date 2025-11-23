"""Claude API service for fact-checking"""
import json
import logging
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta, datetime
from anthropic import Anthropic

logger = logging.getLogger(__name__)


# Prompt template for fact-checking
FACTCHECK_PROMPT = """You are an expert MMT economist reviewing a claim made during the UK Budget speech.

CLAIM: {claim_text}

CONTEXT: {context}

SEVERITY (user-rated 1-10): {severity}

Generate a structured fact-check with the following sections:

1. THE CLAIM: Restate the claim clearly and concisely
2. THE PROBLEM: Explain what is misleading about this framing (1-2 paragraphs)
3. THE REALITY: What is actually true about this situation (2-3 paragraphs)
4. THE EVIDENCE: Specific data, statistics, or sources that support the reality (bullet points with citations)
5. THE MMT PERSPECTIVE: How Modern Monetary Theory reframes this issue (2-3 paragraphs)

Use clear, accessible language. Cite specific sources where possible (ONS, Bank of England, academic papers). Be factual and evidence-based, not rhetorical.

Return as JSON with these exact keys: the_claim, the_problem, the_reality, the_evidence, mmt_perspective, citations (array of objects with title and url).

Important: Return ONLY valid JSON, no other text."""


def generate_fact_check_with_claude(claim, context='', severity=5):
    """
    Generate a fact-check response using Claude API.

    Args:
        claim: The claim text to fact-check
        context: Additional context (optional)
        severity: User-rated severity 1-10

    Returns:
        dict with fact-check data
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = FACTCHECK_PROMPT.format(
        claim_text=claim,
        context=context or 'No additional context provided',
        severity=severity
    )

    try:
        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=settings.CLAUDE_MAX_TOKENS,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        # Extract text from response
        response_text = message.content[0].text if message.content else ''

        # Parse JSON response
        fact_check_data = json.loads(response_text)

        return {
            'the_claim': fact_check_data.get('the_claim', ''),
            'the_problem': fact_check_data.get('the_problem', ''),
            'the_reality': fact_check_data.get('the_reality', ''),
            'the_evidence': fact_check_data.get('the_evidence', ''),
            'mmt_perspective': fact_check_data.get('mmt_perspective', ''),
            'citations': fact_check_data.get('citations', [])
        }

    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        return {
            'the_claim': claim,
            'the_problem': 'Error parsing AI response',
            'the_reality': response_text if 'response_text' in locals() else 'Error generating response',
            'the_evidence': '',
            'mmt_perspective': '',
            'citations': []
        }
    except Exception as e:
        raise Exception(f"Error calling Claude API: {str(e)}")


def process_fact_check_request(request_id):
    """
    Process a fact-check request synchronously.
    This is the actual processing logic, callable without Celery.

    Args:
        request_id: FactCheckRequest ID

    Returns:
        dict with status and response_id or error message
    """
    from .models import FactCheckRequest, FactCheckResponse

    try:
        request = FactCheckRequest.objects.get(id=request_id)
    except FactCheckRequest.DoesNotExist:
        logger.error(f"FactCheckRequest {request_id} not found")
        return {'status': 'error', 'message': 'Request not found'}

    # Update status to processing
    request.status = 'processing'
    request.save()

    try:
        logger.info(f"Starting fact-check processing for request {request_id}")

        # Check if API key is configured
        if not settings.ANTHROPIC_API_KEY:
            raise Exception("ANTHROPIC_API_KEY not configured in settings")

        # Generate fact-check with Claude
        fact_check_data = generate_fact_check_with_claude(
            claim=request.claim_text,
            context=request.context,
            severity=request.severity
        )

        logger.info(f"Fact-check generated successfully for request {request_id}")

        # Create response
        response = FactCheckResponse.objects.create(
            request=request,
            **fact_check_data
        )

        # Update request status
        request.status = 'reviewed'
        request.save()

        logger.info(f"Fact-check saved successfully for request {request_id}")

        return {
            'status': 'success',
            'response_id': response.id
        }

    except Exception as e:
        logger.error(f"Error processing fact-check {request_id}: {str(e)}")

        # Revert status on error
        request.status = 'submitted'
        request.save()

        return {
            'status': 'error',
            'message': str(e)
        }


def get_or_create_user_profile(user):
    """Get or create user profile for fact-checker"""
    from .models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


def award_badge(user, badge_type):
    """Award a badge to a user if they don't already have it"""
    from .models import UserBadge
    badge, created = UserBadge.objects.get_or_create(
        user=user,
        badge_type=badge_type
    )
    return created  # Returns True if new badge was awarded


def check_and_award_badges(user):
    """Check user stats and award appropriate badges"""
    from .models import UserProfile, FactCheckRequest

    profile = get_or_create_user_profile(user)
    profile.update_stats()

    badges_awarded = []

    # First claim
    if profile.total_claims_submitted >= 1:
        if award_badge(user, 'first_claim'):
            badges_awarded.append('first_claim')

    # Prolific checker badges
    if profile.total_claims_submitted >= 50:
        if award_badge(user, 'prolific_checker'):
            badges_awarded.append('prolific_checker')

    if profile.total_claims_submitted >= 100:
        if award_badge(user, 'legendary_checker'):
            badges_awarded.append('legendary_checker')

    # Upvote badges
    if profile.total_upvotes_earned >= 100:
        if award_badge(user, 'upvote_king'):
            badges_awarded.append('upvote_king')

    # Hot streak badges
    if profile.max_hot_streak >= 5:
        if award_badge(user, 'hot_streak_5'):
            badges_awarded.append('hot_streak_5')

    if profile.max_hot_streak >= 10:
        if award_badge(user, 'hot_streak_10'):
            badges_awarded.append('hot_streak_10')

    # Severity accuracy badge
    if profile.severity_accuracy_score >= 90:
        if award_badge(user, 'severity_master'):
            badges_awarded.append('severity_master')

    return badges_awarded


def update_hot_streak(user):
    """Update user's hot streak based on recent submissions"""
    from .models import UserProfile, FactCheckRequest

    profile = get_or_create_user_profile(user)

    # Get user's recent requests in descending order
    recent_requests = FactCheckRequest.objects.filter(
        user=user
    ).order_by('-created_at')[:20]

    if not recent_requests:
        return 0

    # Check for consecutive submissions within 5 minutes
    streak = 1
    for i in range(len(recent_requests) - 1):
        time_diff = recent_requests[i].created_at - recent_requests[i + 1].created_at
        if time_diff <= timedelta(minutes=5):
            streak += 1
        else:
            break

    profile.hot_streak_count = streak
    if streak > profile.max_hot_streak:
        profile.max_hot_streak = streak
    profile.save()

    return streak


def award_experience_points(user, points):
    """Award experience points to a user"""
    from .models import UserProfile

    profile = get_or_create_user_profile(user)
    profile.experience_points += points
    profile.level = profile.calculate_level()
    profile.save()

    return profile.experience_points


def update_claim_of_the_minute():
    """Update claim of the minute tracking"""
    from .models import FactCheckRequest, ClaimOfTheMinute

    # Get current minute timestamp
    now = timezone.now()
    current_minute = now.replace(second=0, microsecond=0)

    # Get claims from the last minute
    one_minute_ago = current_minute - timedelta(minutes=1)
    recent_claims = FactCheckRequest.objects.filter(
        created_at__gte=one_minute_ago,
        created_at__lt=current_minute
    ).order_by('-upvotes').first()

    if recent_claims and recent_claims.upvotes > 0:
        ClaimOfTheMinute.objects.get_or_create(
            request=recent_claims,
            minute_timestamp=current_minute,
            defaults={'upvotes_at_time': recent_claims.upvotes}
        )


def get_live_feed(limit=20):
    """Get live feed of recent claims"""
    from .models import FactCheckRequest

    # Don't prefetch comments if table doesn't exist yet
    try:
        return FactCheckRequest.objects.select_related(
            'user'
        ).prefetch_related(
            'comments'
        ).order_by('-created_at')[:limit]
    except Exception:
        # Fallback without comments if table doesn't exist
        return FactCheckRequest.objects.select_related(
            'user'
        ).order_by('-created_at')[:limit]


def get_leaderboard(timeframe='all'):
    """Get leaderboard of top fact-checkers"""
    from .models import UserProfile

    profiles = UserProfile.objects.select_related('user')

    if timeframe == 'week':
        # Top contributors this week
        profiles = profiles.order_by('-total_claims_submitted')[:10]
    elif timeframe == 'month':
        # Top by upvotes this month
        profiles = profiles.order_by('-total_upvotes_earned')[:10]
    else:
        # All-time leaderboard by XP
        profiles = profiles.order_by('-experience_points')[:10]

    return profiles


def get_claim_stats():
    """Get overall claim statistics"""
    from .models import FactCheckRequest

    total_claims = FactCheckRequest.objects.count()
    claims_today = FactCheckRequest.objects.filter(
        created_at__gte=timezone.now().replace(hour=0, minute=0, second=0)
    ).count()

    high_severity = FactCheckRequest.objects.filter(severity__gte=8).count()

    return {
        'total_claims': total_claims,
        'claims_today': claims_today,
        'high_severity_count': high_severity,
    }
