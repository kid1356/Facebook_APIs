from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Comment)
class CommentBlog(admin.ModelAdmin):
    list_display = ['id','user','text','created_at']

@admin.register(Blogs)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'text', 'get_likes_count']



    def get_likes_count(self, obj):
        return obj.likes.count()

    get_likes_count.short_description = 'Likes Count'

    