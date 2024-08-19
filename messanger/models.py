from django.db import models
from user.models import User
# Create your models here.



class Messages(models.Model):
    CHAT_TYPE = [
        ('private', 'Private'),
        ('group','Group')
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages',null=True, blank= True)
    text = models.TextField(max_length=1000)
    chat_type = models.CharField(max_length=200, choices=CHAT_TYPE, default='group')
    room_name = models.CharField(max_length=200, null=True, blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.sender} to {self.receiver if self.receiver else self.sender}: {self.text}{self.chat_type}'



