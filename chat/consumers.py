import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, Message, CustomUser
from channels.db import database_sync_to_async
import re
from django.utils import timezone

class TeamChat(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        safe_room_name = re.sub(r'[^0-9a-zA-Z_\-\.]', '_', self.room_name)
        self.room_group_name = f'chat_{safe_room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username  # Get sender username
        
        room = await self.get_room(self.room_name)
        await self.save_message(self.scope['user'], room, message)

        #  Send message to room group (broadcast to everyone)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )
    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        
        timestamp = timezone.localtime(timezone.now()).strftime("%H:%M")
        
        # Send message to WebSocket (everyone in room)
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp
        }))
        
    @database_sync_to_async
    def get_room(self, room_name):
    # Automatically create room if it doesn’t exist
        room, created = Room.objects.get_or_create(name=room_name)
        return room


    @database_sync_to_async
    def save_message(self, user, room, message):
        return Message.objects.create(user=user, room=room, content=message)
