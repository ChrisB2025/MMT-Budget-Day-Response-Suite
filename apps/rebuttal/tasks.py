"""Celery tasks for rebuttal generation"""
from celery import shared_task
from django.utils import timezone
from .models import Rebuttal, RebuttalSection
from .services import generate_rebuttal_with_claude


@shared_task
def generate_rebuttal(rebuttal_id, transcript='', priority_claim_ids=None):
    """
    Generate rebuttal sections with Claude API.

    Args:
        rebuttal_id: Rebuttal ID
        transcript: Budget speech transcript
        priority_claim_ids: List of FactCheckRequest IDs

    Returns:
        dict with status and rebuttal_id
    """
    try:
        rebuttal = Rebuttal.objects.get(id=rebuttal_id)
    except Rebuttal.DoesNotExist:
        return {'status': 'error', 'message': 'Rebuttal not found'}

    try:
        # Get priority claims if provided
        priority_claims = []
        if priority_claim_ids:
            from apps.factcheck.models import FactCheckRequest
            claims = FactCheckRequest.objects.filter(id__in=priority_claim_ids)
            priority_claims = [claim.claim_text for claim in claims]

        # Generate rebuttal with Claude
        rebuttal_data = generate_rebuttal_with_claude(
            transcript=transcript,
            priority_claims=priority_claims
        )

        # Create sections
        for section_data in rebuttal_data['sections']:
            RebuttalSection.objects.create(
                rebuttal=rebuttal,
                title=section_data.get('title', 'Section'),
                content=section_data.get('content', ''),
                section_order=section_data.get('order', 1)
            )

        # Mark as published
        rebuttal.published = True
        rebuttal.published_at = timezone.now()
        rebuttal.save()

        return {
            'status': 'success',
            'rebuttal_id': rebuttal.id
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
