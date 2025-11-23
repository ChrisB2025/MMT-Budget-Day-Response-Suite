"""Celery tasks for fact-checking"""
from celery import shared_task
from .services import process_fact_check_request


@shared_task
def process_fact_check(request_id):
    """
    Celery task wrapper for fact-check processing.

    Args:
        request_id: FactCheckRequest ID

    Returns:
        dict with status and response_id
    """
    return process_fact_check_request(request_id)
