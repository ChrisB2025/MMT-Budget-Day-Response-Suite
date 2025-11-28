"""Views for article critique functionality."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Count
from django.utils import timezone
from urllib.parse import quote

from .models import ArticleSubmission, ArticleCritique, QuickResponse, ArticleUpvote
from .forms import ArticleURLSubmitForm, ArticleTextSubmitForm
from .tasks import process_article_submission_task
from .extractors import validate_article_url, detect_publication, SITE_DOMAIN


def build_share_url(submission):
    """Build the shareable URL for a critique."""
    return f"https://{SITE_DOMAIN}/articles/share/{submission.share_id}/"


def article_home(request):
    """Article critique home page with recent critiques."""
    recent_critiques = ArticleSubmission.objects.filter(
        status='completed'
    ).select_related('user', 'critique').order_by('-created_at')[:12]

    # Get stats
    total_critiques = ArticleSubmission.objects.filter(status='completed').count()
    critiques_today = ArticleSubmission.objects.filter(
        status='completed',
        created_at__gte=timezone.now().replace(hour=0, minute=0, second=0)
    ).count()

    # Publication breakdown
    publication_counts = ArticleSubmission.objects.filter(
        status='completed'
    ).values('publication').annotate(count=Count('id')).order_by('-count')[:5]

    return render(request, 'article_critique/home.html', {
        'recent_critiques': recent_critiques,
        'stats': {
            'total': total_critiques,
            'today': critiques_today,
        },
        'publication_counts': publication_counts,
        'sidebar_section': 'article_critique',
        'sidebar_active': 'home',
    })


@login_required
def submit_article_url(request):
    """Submit an article URL for MMT critique."""
    if request.method == 'POST':
        form = ArticleURLSubmitForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False, user=request.user)
            submission.save()

            # Trigger processing
            processing_started = False
            try:
                # Try Celery async processing
                process_article_submission_task.delay(submission.id)
                processing_started = True
                messages.success(
                    request,
                    'Article submitted! Extracting content and generating MMT critique...'
                )
            except Exception:
                # Celery not available - process synchronously
                try:
                    from .services import process_article_submission
                    result = process_article_submission(submission.id)

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
            return redirect('article_critique:detail', share_id=submission.share_id)
    else:
        form = ArticleURLSubmitForm()

    # Get user's recent submissions
    user_submissions = []
    if request.user.is_authenticated:
        user_submissions = ArticleSubmission.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

    return render(request, 'article_critique/submit_url.html', {
        'form': form,
        'user_submissions': user_submissions,
        'sidebar_section': 'article_critique',
        'sidebar_active': 'submit',
    })


@login_required
def submit_article_text(request):
    """Submit article text directly (for paywalled content)."""
    if request.method == 'POST':
        form = ArticleTextSubmitForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False, user=request.user)
            submission.save()

            # Trigger processing
            try:
                process_article_submission_task.delay(submission.id)
                messages.success(
                    request,
                    'Article submitted! Generating MMT critique...'
                )
            except Exception:
                try:
                    from .services import process_article_submission
                    result = process_article_submission(submission.id)

                    if result['status'] == 'success':
                        messages.success(request, 'Critique generated successfully!')
                    else:
                        messages.warning(request, f'Processing issue: {result.get("message", "Unknown error")}')
                except Exception as sync_error:
                    messages.error(request, f'Error: {str(sync_error)}')

            return redirect('article_critique:detail', share_id=submission.share_id)
    else:
        form = ArticleTextSubmitForm()

    return render(request, 'article_critique/submit_text.html', {
        'form': form,
        'sidebar_section': 'article_critique',
        'sidebar_active': 'submit_text',
    })


def article_detail(request, share_id):
    """View a specific article critique (authenticated view)."""
    submission = get_object_or_404(
        ArticleSubmission.objects.select_related('user', 'critique'),
        share_id=share_id
    )

    # Get quick responses
    quick_responses = QuickResponse.objects.filter(article=submission)

    # Check if user has upvoted
    has_upvoted = False
    if request.user.is_authenticated:
        has_upvoted = ArticleUpvote.objects.filter(
            user=request.user,
            article=submission
        ).exists()

    # Increment view count for non-owners
    if not request.user.is_authenticated or request.user != submission.user:
        submission.increment_views()

    # Build shareable URL
    share_url = build_share_url(submission)

    return render(request, 'article_critique/detail.html', {
        'submission': submission,
        'quick_responses': quick_responses,
        'has_upvoted': has_upvoted,
        'share_url': share_url,
        'sidebar_section': 'article_critique',
        'sidebar_active': 'detail',
    })


def public_article_view(request, share_id):
    """Public shareable view of an article critique (no auth required)."""
    submission = get_object_or_404(
        ArticleSubmission.objects.select_related('user', 'critique'),
        share_id=share_id,
        status='completed'
    )

    # Increment view count
    submission.increment_views()

    # Get quick responses
    quick_responses = QuickResponse.objects.filter(article=submission)

    # Build shareable URL
    share_url = build_share_url(submission)

    return render(request, 'article_critique/public_view.html', {
        'submission': submission,
        'quick_responses': quick_responses,
        'share_url': share_url,
    })


@login_required
def article_queue(request):
    """View queue of article submissions."""
    status_filter = request.GET.get('status', 'all')
    publication_filter = request.GET.get('publication', 'all')

    submissions = ArticleSubmission.objects.select_related('user', 'critique')

    if status_filter != 'all':
        submissions = submissions.filter(status=status_filter)

    if publication_filter != 'all':
        submissions = submissions.filter(publication=publication_filter)

    submissions = submissions.order_by('-created_at')[:50]

    return render(request, 'article_critique/queue.html', {
        'submissions': submissions,
        'status_filter': status_filter,
        'publication_filter': publication_filter,
        'publications': ArticleSubmission.PUBLICATION_CHOICES,
        'sidebar_section': 'article_critique',
        'sidebar_active': 'queue',
    })


@login_required
def my_articles(request):
    """View user's own article submissions."""
    submissions = ArticleSubmission.objects.filter(
        user=request.user
    ).select_related('critique').order_by('-created_at')

    return render(request, 'article_critique/my_articles.html', {
        'submissions': submissions,
        'sidebar_section': 'article_critique',
        'sidebar_active': 'my_articles',
    })


@login_required
@require_POST
def upvote_article(request, share_id):
    """Toggle upvote on an article critique."""
    submission = get_object_or_404(ArticleSubmission, share_id=share_id)

    upvote, created = ArticleUpvote.objects.get_or_create(
        user=request.user,
        article=submission
    )

    if not created:
        upvote.delete()
        has_upvoted = False
    else:
        has_upvoted = True

    # Get total upvote count
    upvote_count = ArticleUpvote.objects.filter(article=submission).count()

    # For HTMX requests
    if request.headers.get('HX-Request'):
        return render(request, 'article_critique/partials/upvote_button.html', {
            'submission': submission,
            'has_upvoted': has_upvoted,
            'upvote_count': upvote_count,
        })

    return JsonResponse({
        'has_upvoted': has_upvoted,
        'upvote_count': upvote_count
    })


@login_required
def delete_article(request, share_id):
    """Delete an article submission (owner only)."""
    submission = get_object_or_404(ArticleSubmission, share_id=share_id)

    # Only owner or staff can delete
    if not (request.user.is_staff or submission.user == request.user):
        messages.error(request, 'You do not have permission to delete this article.')
        return redirect('article_critique:home')

    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'Article critique deleted successfully.')
        return redirect('article_critique:my_articles')

    # For HTMX, just delete
    if request.headers.get('HX-Request'):
        submission.delete()
        return HttpResponse(status=200)

    return redirect('article_critique:my_articles')


def preview_article_url(request):
    """AJAX endpoint to preview article URL before submission."""
    url = request.GET.get('url', '').strip()

    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    # Validate URL
    validation = validate_article_url(url)
    if not validation['valid']:
        return JsonResponse({'error': validation['error']}, status=400)

    # Quick fetch to get title/author
    from .extractors import fetch_direct
    content = fetch_direct(url, timeout=15)

    if content.get('error'):
        return JsonResponse({
            'publication': validation['publication'],
            'title': '',
            'author': '',
            'description': '',
            'is_paywalled': content.get('is_paywalled', False),
            'warning': content['error']
        })

    metadata = content.get('metadata', {})
    return JsonResponse({
        'publication': validation['publication'],
        'title': metadata.get('title', ''),
        'author': metadata.get('author', ''),
        'description': metadata.get('description', '')[:300],
        'is_paywalled': content.get('is_paywalled', False),
    })


def get_share_link(request, share_id, platform):
    """Generate share link for a specific platform."""
    submission = get_object_or_404(ArticleSubmission, share_id=share_id, status='completed')

    # Get the quick response for this platform
    try:
        response = QuickResponse.objects.get(article=submission, response_type='tweet')
        share_text = response.content
    except QuickResponse.DoesNotExist:
        share_text = f"Read this MMT critique of '{submission.title}'"

    # Build critique URL
    critique_url = build_share_url(submission)

    # Generate platform-specific share link
    encoded_text = quote(share_text)
    encoded_url = quote(critique_url)

    share_links = {
        'twitter': f"https://twitter.com/intent/tweet?text={encoded_text}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}&quote={encoded_text}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        'reddit': f"https://www.reddit.com/submit?url={encoded_url}&title={encoded_text}",
        'bluesky': f"https://bsky.app/intent/compose?text={encoded_text}%20{encoded_url}",
    }

    share_link = share_links.get(platform, share_links['twitter'])

    return redirect(share_link)


def copy_response_content(request, share_id, response_type):
    """Get response content for copying to clipboard."""
    submission = get_object_or_404(ArticleSubmission, share_id=share_id, status='completed')

    try:
        response = QuickResponse.objects.get(
            article=submission,
            response_type=response_type
        )

        critique_url = build_share_url(submission)

        if response_type == 'thread' and response.thread_parts:
            return JsonResponse({
                'type': 'thread',
                'content': response.content,
                'parts': response.thread_parts,
                'critique_url': critique_url
            })

        return JsonResponse({
            'type': 'single',
            'content': response.content,
            'critique_url': critique_url
        })

    except QuickResponse.DoesNotExist:
        return JsonResponse({'error': 'Response not found'}, status=404)


@login_required
def regenerate_responses(request, share_id):
    """Regenerate quick responses for an article critique."""
    submission = get_object_or_404(ArticleSubmission, share_id=share_id, status='completed')

    # Only owner or staff can regenerate
    if not (request.user.is_staff or submission.user == request.user):
        messages.error(request, 'You do not have permission to regenerate responses.')
        return redirect('article_critique:detail', share_id=share_id)

    try:
        from .services import (
            generate_tweet_response,
            generate_thread_response,
            generate_letter_response
        )
        from .extractors import SITE_DOMAIN

        critique = submission.critique
        critique_url = f"https://{SITE_DOMAIN}/articles/share/{submission.share_id}/"

        # Regenerate tweet
        tweet = generate_tweet_response(
            title=submission.title,
            author=submission.author,
            publication=submission.get_publication_display_name(),
            summary=critique.summary,
            key_issues=critique.quick_rebuttal or critique.summary
        )
        QuickResponse.objects.update_or_create(
            article=submission,
            response_type='tweet',
            defaults={'content': tweet, 'char_count': len(tweet), 'thread_parts': []}
        )

        # Regenerate thread
        thread_parts = generate_thread_response(
            title=submission.title,
            author=submission.author,
            publication=submission.get_publication_display_name(),
            article_url=submission.original_url,
            critique_url=critique_url,
            summary=critique.summary,
            key_claims=critique.key_claims,
            factual_errors=critique.factual_errors,
            framing_issues=critique.framing_issues,
            mmt_analysis=critique.mmt_analysis
        )
        QuickResponse.objects.update_or_create(
            article=submission,
            response_type='thread',
            defaults={
                'content': '\n\n---\n\n'.join(thread_parts),
                'char_count': sum(len(p) for p in thread_parts),
                'thread_parts': thread_parts
            }
        )

        # Regenerate letter
        letter = generate_letter_response(
            title=submission.title,
            author=submission.author,
            publication=submission.get_publication_display_name(),
            date=submission.publication_date.strftime('%d %B %Y') if submission.publication_date else '',
            summary=critique.summary,
            factual_errors=critique.factual_errors,
            corrections=critique.recommended_corrections
        )
        QuickResponse.objects.update_or_create(
            article=submission,
            response_type='letter',
            defaults={'content': letter, 'char_count': len(letter), 'thread_parts': []}
        )

        messages.success(request, 'Responses regenerated successfully!')

    except Exception as e:
        messages.error(request, f'Error regenerating responses: {str(e)}')

    return redirect('article_critique:detail', share_id=share_id)
