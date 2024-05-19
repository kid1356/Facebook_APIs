from django.urls import path
from .views import *
from django.urls import path


urlpatterns = [
    path('create-message/',MessageCreateView.as_view(), name = 'created-messages'),
    # path('get-message/',GetMessageView.as_view(), name = 'get-messages'),
    path('receive-message/',ReceiverView.as_view(), name = 'received-messages'),
    path('delete-message/<int:id>',DeleteMessageView.as_view(), name = 'delete-messages'),
    # path('ws/chat/<int:user_id>/', ChatConsumer.as_asgi()),

]

