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
async def test_analysis(broker, worker):

    analysis_id = str(uuid.uuid4())
    # print('\nSTARTING ANALYSIS:', analysis_id)
    communicator = WebsocketCommunicator(application, f"/ws/analyses/{analysis_id}/")
    connected, subprotocol = await communicator.connect()
    assert connected

    # print('CONNECTED')
    broker.join("default")
    worker.join()

    # Ask it to start
    input_data = {"input_values": json.dumps({"n_iterations": 1, "alpha_range": [0]})}
    await communicator.send_json_to({"action": "ask", **input_data})
    ask_response = await communicator.receive_json_from()  # noqa: F841
    # print('ASKED WITH RESPONSE:', ask_response)
    next_response = await communicator.receive_json_from()  # noqa: F841
    # print('next WITH RESPONSE:', next_response)
    await communicator.disconnect()
