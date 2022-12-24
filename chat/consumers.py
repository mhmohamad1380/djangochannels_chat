import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message, Room


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()


    @database_sync_to_async
    def create_message(self, username, message):
        user = User.objects.filter(username=username).first()
        Message.objects.create(sender=user, message=message)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message",
                                    "message": message, 
                                    "username": self.user.username}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event['username']

        new_message = await self.create_message(username=username, message=message)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "username": username}))