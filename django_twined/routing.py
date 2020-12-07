from django.urls import path

from .consumers import AnalysisConsumer, ServiceConsumer


websocket_urlpatterns = [
    path(r"service/", ServiceConsumer.as_asgi()),
    path(r"analyses/", AnalysisConsumer.as_asgi()),
    path(r"analyses/<uuid:analysis_id>/", AnalysisConsumer.as_asgi()),
]
