from django.urls import path
from chat.consumers import ChatConsumer, WSConsumer, TrackConsumer, NumberOfOnline

websocket_urlpatterns = [
    path('ws/chat/', ChatConsumer.as_asgi()),
    path('ws/realtime/', WSConsumer.as_asgi()),
    path('ws/userlist/', TrackConsumer.as_asgi()),
    path('ws/online_number/', NumberOfOnline.as_asgi()),
]