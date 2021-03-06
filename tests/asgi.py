import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import django_twined.routing


#  TESTS ONLY - this sets up an asgi application for use in async testing of the consumer.
#               The main django application which you're writing an app for will need to set up something similar


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

application = ProtocolTypeRouter(
    {"http": get_asgi_application(), "websocket": URLRouter(django_twined.routing.websocket_urlpatterns)}
)
