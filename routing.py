from django.urls import path
from .consumers import MessageConsumer
from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
    URLRouter(
      [
        path("ws/messages/", MessageConsumer.as_asgi()),
      ]
    )
  ),
})