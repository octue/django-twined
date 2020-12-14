from django.urls import path


websocket_urlpatterns = [
    path(r"my-consumer/", lambda x: x),
]
