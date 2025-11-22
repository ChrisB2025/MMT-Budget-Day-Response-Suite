"""WebSocket routing for bingo app"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/bingo/$', consumers.BingoConsumer.as_asgi()),
]
