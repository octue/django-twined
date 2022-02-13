import logging
import os
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django_twined.messages import ReelMessage
from django_twined.tasks import ask


logger = logging.getLogger(__name__)


class ServiceConsumer(WebsocketConsumer):
    """A high-level consumer allowing subscription to service messages, resource messages and the current twine.

    Resource messages are sent only to a subset of clients (like members of a chat room).

        TODO ACTUALLY GET THIS OUT PROPERLY - Currently uses the default

    ~~ When in danger or in doubt, run in circles, scream and shout ~~

    """

    @property
    def service_name(self):
        """The service name for this connection"""
        # NB We define this as a property so it's an instance attribute, rather than a class attribute, without
        # having to overload __init__.
        return str(self.scope["url_route"]["kwargs"].get("service_name", None))

    @property
    def service_version(self):
        """The service version for this connection

        TODO ACTUALLY GET THIS OUT PROPERLY - Currently uses the default. Figure out a good way of listing the available
         services and versions. Possibly using a service table. Also need to consider the channel layer name which
         should include the version

        """
        # NB We define this as a property so it's an instance attribute, rather than a class attribute, without
        # having to overload __init__.
        return settings.SERVICES[self.service_name]["default_version"]

    @property
    def resource_name(self):
        """The resource group name for this connection, if any"""
        # NB We define this as a property so it's an instance attribute, rather than a class attribute, without
        # having to overload __init__.
        return str(self.scope["url_route"]["kwargs"].get("resource_name", None))

    def connect(self):
        """Accept connection to the service, and send twine to the client as acknowledgement"""

        # The service name should be given in the URL somewhere, if not, don't accept the connection
        if self.service_name is None:
            self.close()

        # Add this channel to the service group (unused at present)
        # async_to_sync(self.channel_layer.group_add)(self.service_name, self.channel_name)

        # Optionally add this channel to a particular resource group, if one is found in the URL kwargs
        if self.resource_name is not None:
            async_to_sync(self.channel_layer.group_add)(self.resource_name, self.channel_name)

        # Accept the connection
        self.accept()

        # Send the twine for this service to the connected client
        #   TODO this might be better done via a conventional view.
        #   TODO Check read-configuration permissions and make the configuration available
        self._send_twine()

    def disconnect(self, code):
        """Accept a disconnection from the service and associated groups gracefully"""

        # Disconnect from the service
        async_to_sync(self.channel_layer.group_discard)(self.service_name, self.channel_name)

        # Disconnect from the resource group, if a member
        if self.resource_name is not None:
            async_to_sync(self.channel_layer.group_discard)(self.resource_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        """Receive service instructions from WebSocket"""

        # Parse the incoming message data
        try:
            message = ReelMessage(src=text_data)
        except Exception:
            ReelMessage(status="error", reference=message.reference, hints="Unable to understand your message").send(
                self
            )
            return

        if message.action == "ping":
            ReelMessage(
                action="pong",
                status="success",
                reference=message.reference,
                hints="U wanna play? I can pong your ping all day.",
            ).send(self)

        if message.action == "ask":

            # Forward the inbound message to the resource group
            if self.resource_name:
                message.group_send(self.resource_name)

            ask(self.service_name, self.service_version, message, self.resource_name or self.channel_name)

            # # Forward the inbount message to the resource group
            # if self.resource_group_name:
            #     ReelMessage(src=text_data, action="asked").group_send(self.resource_group_name)
            #
            #     # TODO more elegant send API for ReelMessage so I can just provide an iterable of group names
            #     #  or *Consumer instances
            #     message.group_send(self.resource_group_name)
            # else:
            #     message.send(self)
            #
            #     # TODO more elegant send API for ReelMessage so I can just provide an iterable of group names
            #     #  or *Consumer instances
            #     message.group_send(self.resource_group_name)
            # else:
            #     message.send(self)
            #

        else:
            ReelMessage(
                action=message.action,
                status="error",
                hint="Unknown action. Perhaps you meant to send the message to the analysis consumer?",
            ).send(self)

    def _send_twine(self):
        """Refresh the client with everything it needs to know about the twine and the analyses it has going on"""

        app_path = settings.TWINED_SERVICES[self.service_name][self.service_version]["path"]
        with open(os.path.join(app_path, "twine.json")) as fp:
            twine = fp.read()

        ReelMessage(action="connect", twine=twine).send(self)
