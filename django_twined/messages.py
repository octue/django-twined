import json
import logging
from time import time
from uuid import uuid4
import django.dispatch
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


logger = logging.getLogger(__name__)

reel_message_sent = django.dispatch.Signal()

channel_layer = get_channel_layer()


MESSAGE_FIELDS = (
    "action",
    "children",
    "configuration_manifest",
    "configuration_values",
    "credentials",
    "data",
    "hints",
    "input_manifest",
    "input_values",
    "logs",
    "output_manifest",
    "output_values",
    "reference",
    "status",
    "timestamp",
    "twine",
    "uuid",
    "value",
)


class ReelMessage:
    """Class to manage incoming and outgoing messages"""

    def __init__(self, src=None, **kwargs):
        """Constructor for ServiceMessage"""
        if src is not None:
            kwargs = {
                **json.loads(src),
                **kwargs,
            }
            # TODO schema based validation with no extra fields allowed

        if "action" not in kwargs.keys():
            raise Exception("No action specified")

        kwargs["status"] = kwargs.pop("status", "success")

        # Check no uuid supplied and create one for this message
        if kwargs.get("uuid", None) is not None:
            raise ValueError("Cannot instantiate a reel message with a UUID. Each message must have a unique UUID.")
        kwargs["uuid"] = str(uuid4())

        # Add a server timestamp
        if kwargs.get("timestamp", None) is not None:
            raise ValueError(
                "Cannot instantiate a reel message with a timestamp. Each message must determine its timestamp."
            )
        kwargs["timestamp"] = time()

        self.__dict__ = dict((k, kwargs.get(k, None)) for k in MESSAGE_FIELDS)

    def serialise(self):
        """Serialise self to a string"""
        to_serialise = dict((k, getattr(self, k)) for k in MESSAGE_FIELDS if getattr(self, k) is not None)
        return json.dumps(to_serialise)

    def send(self, obj):
        """Send this message to an individual channel name
        Also sends a signal allowing 3rd party apps to execute callbacks for certain messages
        """
        serialised = self.serialise()
        logger.debug("Sending ReelMessage to channel '%s': %s", obj, serialised)
        obj.send(serialised)
        reel_message_sent.send(sender=self.__class__, message=self, to_channel=obj, to_group=None)

    def group_send(self, group_name, message_type="reel_message"):
        """Send this message to a group over channels
        Also sends a signal allowing 3rd party apps to execute callbacks for certain messages
        """
        serialised = self.serialise()
        logger.debug("Group sending ReelMessage: %s", serialised)
        async_to_sync(channel_layer.group_send)(group_name, {"type": message_type, "message": serialised})
        reel_message_sent.send(sender=self.__class__, message=self, to_channel=None, to_group=group_name)
