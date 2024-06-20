from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Comment, Blogs, Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from user.models import User

@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        blog = instance.blog
        user = blog.user
        message = f"{instance.user.first_name} commented on your post."
        notification = Notification.objects.create(user=user, message=message)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user.id}",
            {
                "type": "send_notification",
                "notification": notification.message
            }
        )

@receiver(m2m_changed, sender=Blogs.likes.through)
def like_post(sender, instance, action, **kwargs):
    if action == "post_add":
        user = instance.user
        message = f"Someone liked your post."
        notification = Notification.objects.create(user=user, message=message)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user.id}",
            {
                "type": "send_notification",
                "notification": notification.message
            }
        )