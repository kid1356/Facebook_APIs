import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.get_room_group_name(self.room_name)
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.close()
            return "not authenticated"
        
        if not await self.is_user_allowed_in_room(self.room_name, self.user):
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,self.channel_name
        )
        return await super().disconnect(code)
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        await self.channel_layer.group_send(
            self.room_group_name,{
                "type" : "chat_message",
                "message":message,
                "user":str(self.scope["user"])
                }
        )
       # return await super().receive(text_data, bytes_data)
    
    async def chat_message(self,event):
        await self.send(text_data=json.dumps(
            {
                "message":event["message"],
                "user":event["user"]
            }
            ))
        
    def get_room_group_name(self,room_name):
        if room_name.startswith("private_"):
            return f"private_chat_{room_name}"
        
        return f"chat_{room_name}"
    
    @database_sync_to_async
    def is_user_allowed_in_room(self, room_name, user):
        if room_name.startswith("private_"):
            _, user1_id, user2_id = room_name.split('_')
            allowed_users = {int(user1_id), int(user2_id)}
            return user.id in allowed_users
        return True