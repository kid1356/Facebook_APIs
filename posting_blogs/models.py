from django.db import models
from user.models import User
from multiupload.fields import MultiImageField
# Create your models here.

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField(max_length = 1000, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    blog = models.ForeignKey('Blogs', on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"{self.user.first_name}'s comments on {self.created_at}"


class Blogs(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'user_blog')
    images = models.ImageField(upload_to='images/',blank=True, null=True)
    file = models.FileField(blank=True,null=True)
    text = models.TextField(max_length = 1000, null = True, blank=True)
    likes = models.ManyToManyField(User, blank=True, related_name='blog_likes')
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now_add = True)
    is_deleted = models.BooleanField(default = False)

   




