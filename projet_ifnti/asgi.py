"""
ASGI config for projet_ifnti project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # d'autres protocoles comme websocket peuvent être ajoutés ici
})



# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# #import chat.routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet_ifnti.settings')

# django_asgi_app = get_asgi_application()
# application = ProtocolTypeRouter({
#     'http': django_asgi_app,
#     'websocket': AuthMiddlewareStack(
#        # URLRouter(chat.routing.websocket_urlpatterns)
#         ),
# })

