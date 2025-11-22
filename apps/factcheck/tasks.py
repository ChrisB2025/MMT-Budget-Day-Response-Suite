"""Celery tasks for fact-checking"""
from celery import shared_task
from django.utils import timezone
from .models import FactCheckRequest, FactCheckResponse
from .services import generate_fact_check_with_claude


@shared_task
def process_fact_check(request_id):
    """
    Process a fact-check request with Claude API.

    Args:
        request_id: FactCheckRequest ID

    Returns:
        dict with status and response_id
    """
    try:
        request = FactCheckRequest.objects.get(id=request_id)
    except FactCheckRequest.DoesNotExist:
        return {'status': 'error', 'message': 'Request not found'}

    # Update status to processing
    request.status = 'processing'
    request.save()

    try:
        # Generate fact-check with Claude
        fact_check_data = generate_fact_check_with_claude(
            claim=request.claim_text,
            context=request.context,
            severity=request.severity
        )

        # Create response
        response = FactCheckResponse.objects.create(
            request=request,
            **fact_check_data
        )

        # Update request status
        request.status = 'reviewed'
        request.save()

        return {
            'status': 'success',
            'response_id': response.id
        }

    except Exception as e:
        # Revert status on error
        request.status = 'submitted'
        request.save()

        return {
            'status': 'error',
            'message': str(e)
        }
