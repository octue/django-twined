# Disables for testing:
# pylint: disable=missing-docstring

# import dramatiq
# import pytest
# from channels.testing import WebsocketCommunicator
# from django_twined.consumers import ServiceConsumer


# @pytest.fixture
# def broker():
#     broker = dramatiq.get_broker()
#     broker.flush_all()
#     return broker


# @pytest.fixture
# def worker(broker):
#     worker = dramatiq.Worker(broker, worker_timeout=100)
#     worker.start()
#     yield worker
#     worker.stop()


# @pytest.mark.asyncio
# async def test_service_connect(broker, worker):
#     communicator = WebsocketCommunicator(ServiceConsumer, "/ws/service/")
#     connected, subprotocol = await communicator.connect()
#     assert connected

#     # Test that connection prompts return of the twine
#     connect_response = await communicator.receive_json_from()

#     # Test ping pong
#     await communicator.send_json_to({"action": "ping"})
#     ping_response = await communicator.receive_json_from()

#     # Close
#     await communicator.disconnect()

#     # Check responses
#     assert "twine" in connect_response.keys()
#     assert "action" in ping_response.keys()
#     assert ping_response["action"] == "pong"
