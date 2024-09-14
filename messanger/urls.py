from django.urls import path
from .views import *



urlpatterns = [
    path('create-message/',MessageCreateView.as_view(), name = 'created-messages'),
    path('get-message/',GetMessageView.as_view(), name = 'get-messages'),
    path('receive-message/',ReceiverView.as_view(), name = 'received-messages'),
    path('delete-message/<int:id>',DeleteMessageView.as_view(), name = 'delete-messages'),
    path('chat/<str:room_name>/<str:token>/', Group_private_chat_view, name='chat'),
    path('api/private-chat/<int:user_id>/', PrivateChatInitView.as_view(), name='private-chat-init'),

]

