import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
import spotify.consumers

from django.urls import re_path,path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'train.settings')

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            [
            path('lobby/<int:lobby_id>/', spotify.consumers.LobbyConsumer.as_asgi()),
            

            ]
        )
    ),
})
