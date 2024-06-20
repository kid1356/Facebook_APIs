from django.db import models
from user.models import User
# Create your models here.



class Messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField(max_length=1000)
    time_stamp = models.DateTimeField(auto_now_add=True)



