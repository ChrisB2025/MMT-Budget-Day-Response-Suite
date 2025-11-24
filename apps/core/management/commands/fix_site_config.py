"""
Management command to fix Site configuration for django-allauth.
Run with: python manage.py fix_site_config
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Fix Site configuration for django-allauth social login'

    def handle(self, *args, **options):
        self.stdout.write('Fixing Site configuration...')

        # Delete all existing sites
        old_count = Site.objects.count()
        Site.objects.all().delete()
        self.stdout.write(f'  Deleted {old_count} existing site(s)')

        # Create site with ID 1
        site = Site.objects.create(
            id=1,
            domain='mmtaction.uk',
            name='MMT Action'
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created site: {site.id} - {site.domain}'))

        # Update social apps to use this site
        social_apps = SocialApp.objects.all()
        for app in social_apps:
            app.sites.clear()
            app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Updated {app.provider} to use site {site.id}'))

        if not social_apps:
            self.stdout.write(self.style.WARNING('  ! No social applications found'))

        self.stdout.write(self.style.SUCCESS('\n✓ Site configuration fixed successfully!'))
