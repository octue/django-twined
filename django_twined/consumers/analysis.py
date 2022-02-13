import logging
from uuid import uuid4
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.cache import cache
from django_twined.messages import ReelMessage
from django_twined.tasks import ask


logger = logging.getLogger(__name__)


class AnalysisConsumer(WebsocketConsumer):
    """A consumer allowing creation and monitoring of analyses


    ~~ When in danger or in doubt, run in circles, scream and shout ~~


    I want to: load a configuration at startup of the server.
    I want to: load a frontend which knows about my twine and configuration settings.
    I want to: connect my frontend to a backend.
    I want to: supply a backend with input data periodically.
            - I can write a quick python script to do this from local.
    I want to: use the frontend to show some graphic of the most recent input data, continuously updating.
    I want to: use the frontend to show an input form.
    I want to: use the frontend to show an output (disabled) form with results.

    """

    def connect(self):
        """Accept connection to the analysis, and forward any prior messages to the client"""
        self.group_id = str(self.scope["url_route"]["kwargs"].get("analysis_id", uuid4()))

        # Set the group name
        self.group_name = f"analysis-{self.group_id}"

        # Add this channel to the group
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        # Accept the connection
        self.accept()

        # Flush the cache of messages from this group so far
        for message in cache.get(self.group_name, default=list()):
            self.send(text_data=message)

    def disconnect(self, close_code):
        """Accept a disconnection from the analysis gracefully"""
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        """Receive service instructions from WebSocket"""

        # Get the incoming message data
        try:
            message = ReelMessage(src=text_data)
        except Exception as e:
            logger.warning(f"Possible error (or malformed message): {e.args[0]}")
            ReelMessage(status="error", hints="Unable to understand your message").send(self)
            return

        # Attempt to respond
        try:
            # Run a new analysis
            if message.action == "ask":
                ask(self.group_id, message).send(self)

        except Exception as e:
            logger.error(e.args[0])
            ReelMessage(
                action=message.action,
                status="error",
            ).send(self)
            return

        # # Append changes to the cache for this room, allowing us to flush all changes through to new connection
        # # TODO Race condition exists here. Either rewrite automerge for python and keep a master record, or use
        # #  a locking strategy enabling us to ensure all changes are recorded or use a synchronous websocketconsumer
        # #  to properly persist the change history
        # #  https://pypi.org/project/python-redis-lock/
        # #  https://github.com/joanvila/aioredlock
        # changes = cache.get(self.room_name, default=list())
        # changes.append(text_data)
        # cache.set(self.room_name, changes)
        # data = {
        #     "type": "reel_message",
        #     "message": text_data,
        #     "message_bytes": bytes_data,
        # }
        # await self.channel_layer.group_send(self.room_group_name, data)

    def reel_message(self, event):
        """Send a message from the analysis to the client, serialising if necessary"""
        self.send(text_data=event["message"])
