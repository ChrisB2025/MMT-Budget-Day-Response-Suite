"""WebSocket consumers for real-time bingo updates"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class BingoConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time bingo updates"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_group_name = 'bingo_updates'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong'
            }))

    # Handler for square_marked event
    async def square_marked(self, event):
        """Send square marked update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'square_marked',
            'square_id': event['square_id'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    # Handler for bingo_completed event
    async def bingo_completed(self, event):
        """Send bingo completion update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'bingo_completed',
            'user_id': event['user_id'],
            'username': event['username'],
            'card_id': event['card_id'],
            'timestamp': event['timestamp']
        }))

    # Handler for leaderboard_update event
    async def leaderboard_update(self, event):
        """Send leaderboard update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'leaders': event['leaders']
        }))
