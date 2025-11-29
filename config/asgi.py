"""
ASGI config for budget_response_suite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import logging

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()


def get_websocket_application():
    """
    Returns the WebSocket application with graceful fallback.
    If routing import fails (e.g., Redis connection issues), returns None.
    """
    try:
        from apps.bingo import routing as bingo_routing
        return AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    bingo_routing.websocket_urlpatterns
                )
            )
        )
    except Exception as e:
        logger.warning(f"WebSocket routing unavailable: {e}. WebSockets disabled.")
        return None


# Build the protocol router
websocket_app = get_websocket_application()

if websocket_app:
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": websocket_app,
    })
else:
    # HTTP-only mode when WebSocket setup fails
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
    })
