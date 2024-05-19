import os
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from messanger.routing import websocket_patterns 
from .custom_auth import CustomAuthMiddleware



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facebook.settings')


# application  = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http" : get_asgi_application(),
        "websocket" : AllowedHostsOriginValidator(
            CustomAuthMiddleware(
                URLRouter(
                    websocket_patterns
                )
            )
        )
    }
)
