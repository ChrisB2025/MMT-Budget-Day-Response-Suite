# Generated manually to fix Site configuration for django-allauth

from django.db import migrations


def update_site_configuration(apps, schema_editor):
    """Update or create the default site with correct domain and ensure social apps use it"""
    Site = apps.get_model('sites', 'Site')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')

    # Get or create site with ID 1
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': 'mmtaction.uk',
            'name': 'MMT Action'
        }
    )

    # Update if it already existed but had wrong values
    if not created:
        site.domain = 'mmtaction.uk'
        site.name = 'MMT Action'
        site.save()

    # Delete any duplicate sites with the same domain but different ID
    Site.objects.filter(domain='mmtaction.uk').exclude(id=1).delete()

    # Ensure all social apps are associated with site ID 1
    for social_app in SocialApp.objects.all():
        social_app.sites.clear()
        social_app.sites.add(site)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_achievements_user_idx_achievement_user_id_9445b4_idx_and_more'),
        ('sites', '__latest__'),
        ('socialaccount', '__latest__'),
    ]

    operations = [
        migrations.RunPython(update_site_configuration, reverse_code=migrations.RunPython.noop),
    ]
