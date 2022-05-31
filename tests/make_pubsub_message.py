import base64
import json


def make_pubsub_message(
    data,
    publish_time,
    attributes=None,
    message_id=None,
    ordering_key=None,
):
    """Make a json-encodable message replicating the GCP Pub/Sub v1 format
    See: https://cloud.google.com/pubsub/docs/reference/rest/v1/PubsubMessage

    TODO Refactor this into django-gcp, it's for general use testing the events endpoints

    """
    out = dict()

    out["data"] = base64.b64encode(json.dumps(data).encode()).decode()

    iso_us = publish_time.isoformat()
    iso_ns = f"{iso_us}000Z"
    out["publishTime"] = iso_ns

    if attributes is not None:
        # Check all attributes are k-v pairs of strings
        for k, v in attributes.items():
            if k.__class__ != str:
                raise ValueError("All attribute keys must be strings")
            if v.__class__ != str:
                raise ValueError("All attribute values must be strings")
        out["attributes"] = attributes

    if message_id is not None:
        if message_id.__class__ != str:
            raise ValueError("The message_id, if given, must be a string")
        out["messageId"] = message_id

    if ordering_key is not None:
        if ordering_key.__class__ != str:
            raise ValueError("The ordering_key, if given, must be a string")
        out["orderingKey"] = ordering_key

    return out
