import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Messages  # Import the Messages model
from user.models import User


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.room_group_name = self.get_room_group_name(self.room_name)
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        
        if not await self.is_user_allowed_in_room(self.room_name, self.user):
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        await super().disconnect(code)
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to the database
        await self.save_message(self.user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": str(self.user.first_name)
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(
            {
                "message": event["message"],
                "user": event["user"]
            }
        ))

    def get_room_group_name(self, room_name):
        if room_name.startswith("private_"):
            return f"private_chat_{room_name}"
        return f"chat_{room_name}"

    @database_sync_to_async
    def is_user_allowed_in_room(self, room_name, user):
        if room_name.startswith("private_"):
            parts = room_name.split('_')
            if len(parts) == 3:  # private_<user1_id>_<user2_id>
                _, user1_id, user2_id = parts
                allowed_users = {int(user1_id), int(user2_id)}
                return user.id in allowed_users
        return True

    @database_sync_to_async
    def save_message(self, user, message):
        receiver = None
        chat_type = 'group'

        if self.room_name.startswith("private_"):
            parts = self.room_name.split('_')
            if len(parts) == 3:  # private_<user1_id>_<user2_id>
                _, user1_id, user2_id = parts
                if str(user.id) == user1_id:
                    receiver_id = user2_id
                else:
                    receiver_id = user1_id
                
                try:
                    receiver = User.objects.get(id=receiver_id)
                except User.DoesNotExist:
                    # Handle the case where the receiver does not exist
                    return
                chat_type = 'private'
            else:
                # Handle cases where the room name format is not as expected
                return

        
        # Create and save the message
        Messages.objects.create(
            sender=user,
            receiver=receiver,
            text=message,
            chat_type=chat_type,
            room_name=self.room_name
        )
