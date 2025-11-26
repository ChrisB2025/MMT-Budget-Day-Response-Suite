"""Celery tasks for social media critique processing"""
from celery import shared_task


@shared_task
def process_social_critique_task(critique_id):
    """
    Async Celery task to process a social media critique.

    This wraps the synchronous service function to enable
    background processing via Celery.
    """
    from .services import process_social_critique
    return process_social_critique(critique_id)


@shared_task
def cleanup_expired_cache():
    """
    Periodic task to clean up expired content cache entries.

    Should be scheduled to run every few hours via Celery beat.
    """
    from django.utils import timezone
    from .models import ContentCache

    deleted_count, _ = ContentCache.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()

    return f'Deleted {deleted_count} expired cache entries'


@shared_task
def regenerate_critique_replies(critique_id):
    """
    Async task to regenerate shareable replies for a critique.

    Useful when the reply generation logic is updated or
    when replies need to be refreshed.
    """
    from .models import SocialMediaCritique
    from .services import _generate_and_save_replies

    try:
        critique = SocialMediaCritique.objects.select_related('response').get(
            id=critique_id,
            status='completed'
        )
    except SocialMediaCritique.DoesNotExist:
        return {'status': 'error', 'message': 'Critique not found or not completed'}

    if not hasattr(critique, 'response'):
        return {'status': 'error', 'message': 'No response exists for this critique'}

    # Build a placeholder URL (the actual URL will be relative)
    critique_url = f"/critique/{critique.share_id}/"

    try:
        # Regenerate for original platform
        _generate_and_save_replies(
            critique, critique.response, critique.platform, critique_url
        )

        # Also for Twitter if different
        if critique.platform != 'twitter':
            _generate_and_save_replies(
                critique, critique.response, 'twitter', critique_url
            )

        return {'status': 'success', 'message': 'Replies regenerated'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
