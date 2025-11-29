"""Context processors for MMT Campaign Suite"""
from django.conf import settings


def mmt_settings(request):
    """
    Add MMT Campaign Suite settings to template context.
    """
    return {
        'MMT_DISCORD_INVITE_URL': getattr(settings, 'MMT_DISCORD_INVITE_URL', 'https://discord.gg/DXn9rxt9bh'),
        'KEYSTROKE_KINGDOM_URL': getattr(settings, 'KEYSTROKE_KINGDOM_URL', 'https://keystroke.mmtaction.uk/'),
        'MMT_SITE_NAME': getattr(settings, 'MMT_SITE_NAME', 'MMT Campaign Suite'),
        'MMT_SITE_TAGLINE': getattr(settings, 'MMT_SITE_TAGLINE', 'Track economic myths in real time, crowdsource fact checks, hold media accountable, and generate shareable MMT rebuttals.'),
        'MMT_DEFAULT_HASHTAG': getattr(settings, 'MMT_DEFAULT_HASHTAG', '#mmt'),
    }
