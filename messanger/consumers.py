import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Messages  
from user.models import User
import os
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile
import base64


online_users = set()

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        self.key = os.getenv('ENCRYPTION_KEY').encode()  #getting encription key
        self.cipher_suite = Fernet(self.key)       
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')    #getting room from url
        self.room_group_name = self.get_room_group_name(self.room_name)    #quering if room is private or group
        self.user = self.scope["user"]

      
        if not self.user.is_authenticated:
            await self.close()             #authenticated user only
            return "not authenticated"
        
        online_users.add(self.user.id)         #adding users to set when they are online
        print("userss.............",online_users)

        if not await self.is_user_allowed_in_room(self.room_name, self.user):
            await self.close()             #if user allowed in private room
            return  "You are not allowed in this room"
        
       
        await self.channel_layer.group_add(self.room_group_name, self.channel_name ) #adding group 
           
        print(f"User {self.user} connected to room {self.room_name}")
        await self.accept()
 
        try:
            if self.room_name.startswith('private_'):   #see if room private or Group
                all_messages = await self.get_unread_message(self.user,self.room_name)  
            else:
                all_messages = await self.get_all_group_messages(self.room_name)
        
            if not all_messages:
                print("No messages found")
            else:
                print(f"Found {len(all_messages)} messages")
            
            for message in all_messages:
                await self.get_sender_name(message)  #get sender name
                await self.get_message_text(message)  # get sender message
              
                await self.send_unread_message(message)  # Send the unread message
                await self.mark_as_read(message)  #  mark as read

        except Exception as e:
             print(f"Error processing messages: {e}")




    async def disconnect(self, code):

        if self.user.id in online_users:
            online_users.remove(self.user.id)     #removing user from set when they disconnect

        # Remove the user from the room group when they disconnect
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await super().disconnect(code)
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)    #receiving message
        message = text_data_json.get('message','')
        file_data = text_data_json.get('file',None)
        file_name = text_data_json.get('fileName', None)

         
        

       
        # encrypting the received message
        try:
            encrypted_message = self.encrypt_message(message)
        except Exception as e:
            print(f'Encryption failed: {e}')
            return 
        
        
        if self.room_name.startswith("private_"):
            parts = self.room_name.split('_')
            if len(parts) == 3:  # private_<user1_id>_<user2_id>
                _, user1_id, user2_id = parts
                if str(self.user.id) == user1_id:
                    receiver_id = user2_id
                    
                else:
                    receiver_id = user1_id
                    
                 
        
            receiver_user=await self.get_user_by_id(receiver_id)
       

            if self.user_isOnline(receiver_user.id):
                is_read = True
               
            else:
                is_read = False

            


            message =  await self.save_message(self.user, message,file_data,file_name,is_read)
        else:
 
            message = await self.save_message(self.user, message,file_data,file_name,is_read = False)
 

           
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": encrypted_message,
                "user": str(self.user.first_name),
                "file":file_data,
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
                "user": event["user"],
                "file": event.get("file"),
            }
        ))

    async def send_unread_message(self,message):                # sending unread messages to web socket
        encrypted_message = self.encrypt_message(message.text)          
        decrypted_message = self.decrypt_message(encrypted_message)
        
        file = message.file.url if message.file else None


        await self.send(text_data=json.dumps(
            {
                "message":decrypted_message,
                "user": str(message.sender.first_name),
                "file":file

            }
        ))



    def encrypt_message(self, message):   # method for encrypting messages
        try:                         
            encrypted = self.cipher_suite.encrypt(message.encode()).decode()

            return encrypted
        except Exception as e:
            print(f'Encryption error: {e}')
            raise

    def decrypt_message(self, encrypted_message): # method for decrypting messages
        try:
         
            decrypted = self.cipher_suite.decrypt(encrypted_message.encode()).decode()
   
            return decrypted
        except Exception as e:
            print(f'Decryption error: {e}')
            raise

    def get_room_group_name(self, room_name):
        if room_name.startswith("private_"):
            return f"private_chat_{room_name}"     #getting group or private rooms
        return f"chat_{room_name}"


    def user_isOnline(self,user_id):
        if user_id in online_users:
            return True                     # checking if user is in set()
        else:
            return False

    @database_sync_to_async
    def is_user_allowed_in_room(self, room_name, user):
        if room_name.startswith("private_"):
            parts = room_name.split('_')                              #checking the user is allowed in room also is user is authenticated
            if len(parts) == 3:  # private_<user1_id>_<user2_id>
                _, user1_id, user2_id = parts
                allowed_users = {int(user1_id), int(user2_id)}
                return user.id in allowed_users
        return True

    @database_sync_to_async
    def save_message(self, user, message,file_data,file_name, is_read):
        receiver = None
        chat_type = 'group'
        file = None
        
        
        if file_data:
            file_format, filestr = file_data.split(';base64,')
            extension = file_format.split('/')[-1]
            original_file_name = file_name if file_name else f'default_file.{extension}'

            file = ContentFile(base64.b64decode(filestr), name=original_file_name)




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
                
                return "room format is not proper or not found"
            
             #saving the mesasges in the database
        Messages.objects.create(
            sender=user,
            receiver=receiver,
            text=message,
            chat_type=chat_type,
            room_name=self.room_name,
            is_read = is_read,
            file = file

        )

    @database_sync_to_async
    def get_unread_message(self, user,room_name):       #filtering the unread messages
        return list(Messages.objects.filter(receiver =user,room_name=room_name, is_read = False).order_by('time_stamp'))
    
    
    @database_sync_to_async
    def mark_as_read(self,message):     # update the fields is_read
        message.is_read = True
        message.save()
    

    @database_sync_to_async
    def get_sender_name(self, message):      # getting the sender name
        return message.sender.first_name      

    @database_sync_to_async
    def get_message_text(self, message):    # getting the sender message
        return message.text

    @database_sync_to_async 
    def get_all_group_messages(self,room_name):           #geeting all group messages in room(group)
        return list(Messages.objects.filter(room_name=room_name, is_read= False).order_by('time_stamp'))
    
    @database_sync_to_async
    def get_user_by_id(self,user_id):       #getting user by id 
        try:
            user = User.objects.get(id = user_id)     
            return user
        except User.DoesNotExist:
            return None

        
