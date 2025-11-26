"""Views for social media critique functionality"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from urllib.parse import quote

from .models import SocialMediaCritique, CritiqueResponse, ShareableReply, CritiqueUpvote
from .forms import SocialCritiqueSubmitForm
from .tasks import process_social_critique_task
from .fetchers import validate_url, fetch_url_content, detect_platform, SITE_DOMAIN


def build_share_url(critique, request=None):
    """
    Build the shareable URL for a critique using the configured domain.

    Args:
        critique: SocialMediaCritique instance
        request: Optional request object (not used but kept for compatibility)

    Returns:
        Full shareable URL string
    """
    return f"https://{SITE_DOMAIN}/critique/share/{critique.share_id}/"


def critique_home(request):
    """Social critique home page with recent critiques"""
    recent_critiques = SocialMediaCritique.objects.filter(
        status='completed'
    ).select_related('user', 'response').order_by('-created_at')[:12]

    # Get stats
    total_critiques = SocialMediaCritique.objects.filter(status='completed').count()
    critiques_today = SocialMediaCritique.objects.filter(
        status='completed',
        created_at__gte=timezone.now().replace(hour=0, minute=0, second=0)
    ).count()

    # Platform breakdown
    platform_counts = SocialMediaCritique.objects.filter(
        status='completed'
    ).values('platform').annotate(count=Count('id')).order_by('-count')[:5]

    return render(request, 'social_critique/home.html', {
        'recent_critiques': recent_critiques,
        'stats': {
            'total': total_critiques,
            'today': critiques_today,
        },
        'platform_counts': platform_counts,
        'sidebar_section': 'social_critique',
        'sidebar_active': 'home',
    })


@login_required
def submit_critique(request):
    """Submit a social media URL for MMT critique"""
    if request.method == 'POST':
        form = SocialCritiqueSubmitForm(request.POST)
        if form.is_valid():
            critique = form.save(commit=False, user=request.user)
            critique.save()

            # Trigger processing
            processing_started = False
            try:
                # Try Celery async processing
                process_social_critique_task.delay(critique.id)
                processing_started = True
                messages.success(
                    request,
                    'URL submitted! Fetching content and generating MMT critique...'
                )
            except Exception as e:
                # Celery not available - process synchronously
                try:
                    from .services import process_social_critique
                    result = process_social_critique(critique.id)

                    if result['status'] == 'success':
                        processing_started = True
                        messages.success(request, 'Critique generated successfully!')
                    else:
                        messages.warning(
                            request,
                            f'Processing issue: {result.get("message", "Unknown error")}'
                        )
                except Exception as sync_error:
                    messages.error(request, f'Error: {str(sync_error)}')

            # Redirect to detail page
            return redirect('social_critique:detail', share_id=critique.share_id)
    else:
        form = SocialCritiqueSubmitForm()

    # Get user's recent critiques
    user_critiques = []
    if request.user.is_authenticated:
        user_critiques = SocialMediaCritique.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

    return render(request, 'social_critique/submit.html', {
        'form': form,
        'user_critiques': user_critiques,
        'sidebar_section': 'social_critique',
        'sidebar_active': 'submit',
    })


def critique_detail(request, share_id):
    """View a specific critique (authenticated view)"""
    critique = get_object_or_404(
        SocialMediaCritique.objects.select_related('user', 'response'),
        share_id=share_id
    )

    # Get shareable replies
    shareable_replies = ShareableReply.objects.filter(critique=critique)

    # Check if user has upvoted
    has_upvoted = False
    if request.user.is_authenticated:
        has_upvoted = CritiqueUpvote.objects.filter(
            user=request.user,
            critique=critique
        ).exists()

    # Increment view count for non-owners
    if not request.user.is_authenticated or request.user != critique.user:
        critique.increment_views()

    # Build shareable URL using mmtaction.uk domain
    share_url = build_share_url(critique)

    return render(request, 'social_critique/detail.html', {
        'critique': critique,
        'shareable_replies': shareable_replies,
        'has_upvoted': has_upvoted,
        'share_url': share_url,
        'sidebar_section': 'social_critique',
        'sidebar_active': 'detail',
    })


def public_critique_view(request, share_id):
    """Public shareable view of a critique (no auth required)"""
    critique = get_object_or_404(
        SocialMediaCritique.objects.select_related('user', 'response'),
        share_id=share_id,
        status='completed'
    )

    # Increment view count
    critique.increment_views()

    # Get shareable replies
    shareable_replies = ShareableReply.objects.filter(critique=critique)

    # Build shareable URL using mmtaction.uk domain
    share_url = build_share_url(critique)

    return render(request, 'social_critique/public_view.html', {
        'critique': critique,
        'shareable_replies': shareable_replies,
        'share_url': share_url,
    })


@login_required
def critique_queue(request):
    """View queue of critiques"""
    status_filter = request.GET.get('status', 'all')
    platform_filter = request.GET.get('platform', 'all')

    critiques = SocialMediaCritique.objects.select_related('user', 'response')

    if status_filter != 'all':
        critiques = critiques.filter(status=status_filter)

    if platform_filter != 'all':
        critiques = critiques.filter(platform=platform_filter)

    critiques = critiques.order_by('-created_at')[:50]

    # Get platform choices for filter
    platforms = SocialMediaCritique.PLATFORM_CHOICES

    return render(request, 'social_critique/queue.html', {
        'critiques': critiques,
        'status_filter': status_filter,
        'platform_filter': platform_filter,
        'platforms': platforms,
        'sidebar_section': 'social_critique',
        'sidebar_active': 'queue',
    })


@login_required
@require_POST
def upvote_critique(request, share_id):
    """Toggle upvote on a critique"""
    critique = get_object_or_404(SocialMediaCritique, share_id=share_id)

    upvote, created = CritiqueUpvote.objects.get_or_create(
        user=request.user,
        critique=critique
    )

    if not created:
        # Already upvoted, remove it
        upvote.delete()
        has_upvoted = False
    else:
        has_upvoted = True

    # Get total upvote count
    upvote_count = CritiqueUpvote.objects.filter(critique=critique).count()

    # For HTMX requests
    if request.headers.get('HX-Request'):
        return render(request, 'social_critique/partials/upvote_button.html', {
            'critique': critique,
            'has_upvoted': has_upvoted,
            'upvote_count': upvote_count,
        })

    return JsonResponse({
        'has_upvoted': has_upvoted,
        'upvote_count': upvote_count
    })


def preview_url(request):
    """AJAX endpoint to preview URL content before submission"""
    url = request.GET.get('url', '').strip()

    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    # Validate URL
    validation = validate_url(url)
    if not validation['valid']:
        return JsonResponse({'error': validation['error']}, status=400)

    # Fetch content
    content = fetch_url_content(url, timeout=15)

    if content.get('error'):
        return JsonResponse({'error': content['error']}, status=400)

    return JsonResponse({
        'platform': content.get('platform', 'other'),
        'title': content.get('title', ''),
        'author': content.get('author', ''),
        'description': content.get('description', '')[:300],
        'thumbnail_url': content.get('thumbnail_url', ''),
    })


def get_share_link(request, share_id, platform):
    """Generate share link for a specific platform and redirect to it"""
    critique = get_object_or_404(SocialMediaCritique, share_id=share_id, status='completed')

    # Get the shareable reply for this platform
    try:
        reply = ShareableReply.objects.get(
            critique=critique,
            reply_type='short',
            platform_target=platform
        )
        share_text = reply.content
    except ShareableReply.DoesNotExist:
        # Fallback text
        share_text = f"Check out this MMT analysis of a {critique.get_platform_display()} post"

    # Build critique URL using mmtaction.uk domain
    critique_url = build_share_url(critique)

    # Generate platform-specific share link
    encoded_text = quote(share_text)
    encoded_url = quote(critique_url)

    share_links = {
        'twitter': f"https://twitter.com/intent/tweet?text={encoded_text}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}&quote={encoded_text}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        'reddit': f"https://www.reddit.com/submit?url={encoded_url}&title={encoded_text}",
        'threads': f"https://threads.net/intent/post?text={encoded_text}%20{encoded_url}",
        'bluesky': f"https://bsky.app/intent/compose?text={encoded_text}%20{encoded_url}",
        'mastodon': f"https://mastodon.social/share?text={encoded_text}%20{encoded_url}",
        'youtube': f"https://twitter.com/intent/tweet?text={encoded_text}",  # YouTube doesn't have share intent, use Twitter
    }

    share_link = share_links.get(platform, share_links['twitter'])

    # Redirect to the share link
    return redirect(share_link)


def copy_reply_content(request, share_id, reply_type, platform):
    """Get reply content for copying to clipboard"""
    critique = get_object_or_404(SocialMediaCritique, share_id=share_id, status='completed')

    try:
        reply = ShareableReply.objects.get(
            critique=critique,
            reply_type=reply_type,
            platform_target=platform
        )

        # Build critique URL using mmtaction.uk domain
        critique_url = build_share_url(critique)

        # For threads, return the thread parts
        if reply_type == 'thread' and reply.thread_parts:
            # Add critique URL to last post if not present
            thread_parts = reply.thread_parts.copy()
            if critique_url not in thread_parts[-1]:
                thread_parts[-1] += f"\n\n{critique_url}"

            return JsonResponse({
                'type': 'thread',
                'content': reply.content,
                'parts': thread_parts,
                'critique_url': critique_url
            })

        # For short replies, ensure URL is included
        content = reply.content
        if critique_url not in content:
            content = f"{content}\n\n{critique_url}"

        return JsonResponse({
            'type': 'single',
            'content': content,
            'critique_url': critique_url
        })

    except ShareableReply.DoesNotExist:
        return JsonResponse({'error': 'Reply not found'}, status=404)


@login_required
def my_critiques(request):
    """View user's own critiques"""
    critiques = SocialMediaCritique.objects.filter(
        user=request.user
    ).select_related('response').order_by('-created_at')

    return render(request, 'social_critique/my_critiques.html', {
        'critiques': critiques,
        'sidebar_section': 'social_critique',
        'sidebar_active': 'my_critiques',
    })


@login_required
def delete_critique(request, share_id):
    """Delete a critique (owner only)"""
    critique = get_object_or_404(SocialMediaCritique, share_id=share_id)

    # Only owner or staff can delete
    if not (request.user.is_staff or critique.user == request.user):
        messages.error(request, 'You do not have permission to delete this critique.')
        return redirect('social_critique:home')

    if request.method == 'POST':
        critique.delete()
        messages.success(request, 'Critique deleted successfully.')
        return redirect('social_critique:my_critiques')

    # For HTMX, just delete
    if request.headers.get('HX-Request'):
        critique.delete()
        return HttpResponse(status=200)

    return redirect('social_critique:my_critiques')


@login_required
def regenerate_replies(request, share_id):
    """Regenerate shareable replies for a critique with optional suggestions"""
    critique = get_object_or_404(SocialMediaCritique, share_id=share_id, status='completed')

    # Only owner or staff can regenerate
    if not (request.user.is_staff or critique.user == request.user):
        messages.error(request, 'You do not have permission to regenerate replies.')
        return redirect('social_critique:detail', share_id=share_id)

    # Get suggestions from POST data if provided
    suggestions = request.POST.get('suggestions', '').strip() if request.method == 'POST' else ''

    try:
        from .services import _generate_and_save_replies_with_suggestions
        critique_url = build_share_url(critique)

        # Regenerate for original platform
        _generate_and_save_replies_with_suggestions(
            critique, critique.response, critique.platform, critique_url, suggestions
        )

        # Also for Twitter if different
        if critique.platform != 'twitter':
            _generate_and_save_replies_with_suggestions(
                critique, critique.response, 'twitter', critique_url, suggestions
            )

        messages.success(request, 'Replies regenerated successfully!')
    except Exception as e:
        messages.error(request, f'Error regenerating replies: {str(e)}')

    return redirect('social_critique:detail', share_id=share_id)
