import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.close()
            return "not authenticated"
        
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
            self.room_group_name,{"type" : "chat_message","message":message,"user":str(self.scope["user"])}
        )
       # return await super().receive(text_data, bytes_data)
    
    async def chat_message(self,event):
        await self.send(text_data=json.dumps({"message":event["message"],"user":event["user"]}))