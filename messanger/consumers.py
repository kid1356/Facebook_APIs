import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Messages  # Import the Messages model
from user.models import User
import os
from cryptography.fernet import Fernet

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Load the encryption key from the environment variable and initialize the cipher suite
        self.key = os.getenv('ENCRYPTION_KEY').encode()
        self.cipher_suite = Fernet(self.key)
    
    async def connect(self):
        # Get room name and user from the scope
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.room_group_name = self.get_room_group_name(self.room_name)
        self.user = self.scope["user"]

        # Ensure the user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if the user is allowed in the room
        if not await self.is_user_allowed_in_room(self.room_name, self.user):
            await self.close()
            return
        
        # Add the user to the room group and accept the WebSocket connection
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        # Remove the user from the room group when they disconnect
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        await super().disconnect(code)
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']


        # encrypting the received message
        try:
            encrypted_message = self.encrypt_message(message)
        except Exception as e:
            print(f'Encryption failed: {e}')
            return 
        
        await self.save_message(self.user, message)

           
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": encrypted_message,
                "user": str(self.user.first_name)
            }
        )
    
    async def chat_message(self, event):
        # Decrypt the message before sending it to the WebSocket

        encrypted_message = event["message"]
        try:
            decrypted_message = self.decrypt_message(encrypted_message)
        except Exception as e:
            print(f'Decryption error in chat_message: {e}')
            return


        # Send the decrypted message to the WebSocket client
        await self.send(text_data=json.dumps(
            {
                "message": decrypted_message,
                "user": event["user"]
            }
        ))

    def encrypt_message(self, message):
        try:
            encrypted = self.cipher_suite.encrypt(message.encode()).decode()

            return encrypted
        except Exception as e:
            print(f'Encryption error: {e}')
            raise

    def decrypt_message(self, encrypted_message):
        try:
         
            decrypted = self.cipher_suite.decrypt(encrypted_message.encode()).decode()
   
            return decrypted
        except Exception as e:
            print(f'Decryption error: {e}')
            raise

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

