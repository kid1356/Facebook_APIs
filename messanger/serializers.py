from .models import *
from rest_framework import serializers

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    class Meta:
        model = Messages
        fields = ['sender','sender_name','receiver','receiver_name','text','time_stamp','file']

    
    def get_sender_name(self,obj):
        sender = obj.sender
        return sender.first_name if sender else None
    
    def get_receiver_name(self,obj):
        receiver = obj.receiver
        return receiver.first_name if receiver else None
