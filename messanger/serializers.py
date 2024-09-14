from .models import *
from rest_framework import serializers

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    class Meta:
        model = Messages
        fields = ['sender','sender_name','receiver','text','time_stamp','images','file']

    
    def get_sender_name(self,obj):
        sender = obj.sender
        return sender.first_name if sender else None
