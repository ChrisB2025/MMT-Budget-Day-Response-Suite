"""
Management command to process stuck fact-check requests.

Usage:
    python manage.py process_stuck_factchecks
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.factcheck.models import FactCheckRequest
from apps.factcheck.services import process_fact_check_request


class Command(BaseCommand):
    help = 'Process fact-check requests that are stuck in submitted/processing status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Maximum number of requests to process',
        )
        parser.add_argument(
            '--status',
            type=str,
            default='all',
            choices=['submitted', 'processing', 'all'],
            help='Which status to process (default: all)',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        status = options['status']

        # Get stuck requests
        if status == 'all':
            requests = FactCheckRequest.objects.filter(
                Q(status='submitted') | Q(status='processing')
            ).order_by('created_at')
        else:
            requests = FactCheckRequest.objects.filter(
                status=status
            ).order_by('created_at')

        if limit:
            requests = requests[:limit]

        total = requests.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS('No stuck requests found!'))
            return

        self.stdout.write(f'Found {total} stuck request(s). Processing...\n')

        success_count = 0
        error_count = 0

        for request in requests:
            self.stdout.write(f'Processing request #{request.id}: {request.claim_text[:50]}...')

            try:
                result = process_fact_check_request(request.id)

                if result['status'] == 'success':
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Success! Response ID: {result["response_id"]}'))
                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'  ✗ Error: {result["message"]}'))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Exception: {str(e)}'))

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Processed {success_count} successfully'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Failed {error_count} requests'))
