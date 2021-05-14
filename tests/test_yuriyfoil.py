import json
import uuid
import dramatiq
import pytest
from channels.testing import WebsocketCommunicator

from tests.test_server.routing import application


@pytest.fixture
def broker():
    broker = dramatiq.get_broker()
    broker.flush_all()
    return broker


@pytest.fixture
def worker(broker):
    worker = dramatiq.Worker(broker, worker_timeout=100)
    worker.start()
    yield worker
    worker.stop()


@pytest.mark.asyncio
async def test_yuriyfoil(broker, worker):

    analysis_id = str(uuid.uuid4())
    print("\nSTARTING ANALYSIS:", analysis_id)
    communicator = WebsocketCommunicator(application, f"/ws/analyses/{analysis_id}/")
    connected, subprotocol = await communicator.connect()
    assert connected

    print("CONNECTED")
    broker.join("default")
    worker.join()

    # Send it something that doesn't validate and watch it fail
    # input_data = {"input_values": json.dumps({"alph_range": [0]})}  # <--- typo in the dict key
    # await communicator.send_json_to({"action": "ask", **input_data})
    # ask_confirm = await communicator.receive_json_from()  # noqa: F841
    # print('ASK CONFIRMATION:', ask_confirm)
    # ask_start_notification = await communicator.receive_json_from()  # noqa: F841
    # print('ask_start_notification:', ask_start_notification)
    # ask_end_notification = await communicator.receive_json_from()  # noqa: F841
    # assert "twined.exceptions.InvalidValuesContents: 'alpha_range' is a required property" in ask_end_notification['hints']

    # Ask it to start
    input_data = {"input_values": json.dumps({"alpha_range": [0]})}
    await communicator.send_json_to({"action": "ask", **input_data})
    ask_confirm = await communicator.receive_json_from()  # noqa: F841
    print("ASK CONFIRMATION:", ask_confirm)
    ask_start_notification = await communicator.receive_json_from()  # noqa: F841
    print("ask_start_notification:", ask_start_notification)
    ask_end_notification = await communicator.receive_json_from(timeout=10)  # noqa: F841
    print("ask_end_notification:", ask_end_notification)
    await communicator.disconnect()
