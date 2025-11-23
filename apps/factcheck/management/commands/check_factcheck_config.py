"""
Diagnostic command to check fact-check configuration.

Usage:
    python manage.py check_factcheck_config
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from celery import current_app
import redis


class Command(BaseCommand):
    help = 'Check fact-check configuration and diagnose issues'

    def handle(self, *args, **options):
        self.stdout.write('='*60)
        self.stdout.write('FACT-CHECK CONFIGURATION DIAGNOSTIC')
        self.stdout.write('='*60)

        # 1. Check Anthropic API Key
        self.stdout.write('\n1. Checking Anthropic API Key...')
        if settings.ANTHROPIC_API_KEY:
            key_preview = settings.ANTHROPIC_API_KEY[:15] + '...' if len(settings.ANTHROPIC_API_KEY) > 15 else settings.ANTHROPIC_API_KEY
            self.stdout.write(self.style.SUCCESS(f'   ✓ API Key configured: {key_preview}'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ ANTHROPIC_API_KEY is NOT set!'))
            self.stdout.write('   → Set ANTHROPIC_API_KEY in your environment variables')

        # 2. Check Redis Connection
        self.stdout.write('\n2. Checking Redis Connection...')
        self.stdout.write(f'   Broker URL: {settings.CELERY_BROKER_URL}')

        try:
            # Try to connect to Redis
            r = redis.from_url(settings.CELERY_BROKER_URL)
            r.ping()
            self.stdout.write(self.style.SUCCESS('   ✓ Redis connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Redis connection failed: {str(e)}'))
            self.stdout.write('   → Check REDIS_URL and CELERY_BROKER_URL settings')

        # 3. Check Celery Configuration
        self.stdout.write('\n3. Checking Celery Configuration...')
        self.stdout.write(f'   Broker: {current_app.conf.broker_url}')
        self.stdout.write(f'   Backend: {current_app.conf.result_backend}')

        # Check if tasks are registered
        registered_tasks = list(current_app.tasks.keys())
        fact_check_tasks = [t for t in registered_tasks if 'fact' in t.lower()]

        if fact_check_tasks:
            self.stdout.write(self.style.SUCCESS(f'   ✓ Found {len(fact_check_tasks)} fact-check task(s):'))
            for task in fact_check_tasks:
                self.stdout.write(f'     - {task}')
        else:
            self.stdout.write(self.style.WARNING('   ⚠ No fact-check tasks found in registry'))

        # 4. Check pending claims
        self.stdout.write('\n4. Checking Pending Claims...')
        from apps.factcheck.models import FactCheckRequest

        submitted = FactCheckRequest.objects.filter(status='submitted').count()
        processing = FactCheckRequest.objects.filter(status='processing').count()
        reviewed = FactCheckRequest.objects.filter(status='reviewed').count()

        self.stdout.write(f'   Submitted: {submitted}')
        self.stdout.write(f'   Processing: {processing}')
        self.stdout.write(f'   Reviewed: {reviewed}')

        if submitted > 0 or processing > 0:
            self.stdout.write(self.style.WARNING(f'   ⚠ {submitted + processing} claim(s) need processing'))

        # 5. Try a test API call
        self.stdout.write('\n5. Testing Claude API...')
        if settings.ANTHROPIC_API_KEY:
            try:
                from anthropic import Anthropic
                client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

                # Simple test message
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=50,
                    messages=[{"role": "user", "content": "Say 'test successful'"}]
                )

                self.stdout.write(self.style.SUCCESS('   ✓ Claude API test successful'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✗ Claude API test failed: {str(e)}'))
        else:
            self.stdout.write(self.style.ERROR('   ✗ Skipped (no API key)'))

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('RECOMMENDATIONS:')
        self.stdout.write('='*60)

        if not settings.ANTHROPIC_API_KEY:
            self.stdout.write('1. Set ANTHROPIC_API_KEY environment variable')

        if submitted > 0 or processing > 0:
            self.stdout.write('2. Run: python manage.py process_stuck_factchecks')

        self.stdout.write('3. Check Celery worker logs for errors')
        self.stdout.write('4. Verify Celery worker is running: celery -A config inspect active')
        self.stdout.write('')
