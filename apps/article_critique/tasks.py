"""Celery tasks for async article processing."""
from celery import shared_task
from .services import process_article_submission


@shared_task
def process_article_submission_task(submission_id: int):
    """
    Celery task wrapper for article submission processing.

    Args:
        submission_id: ArticleSubmission database ID

    Returns:
        Dictionary with status and message
    """
    return process_article_submission(submission_id)
