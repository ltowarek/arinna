import asyncio
import threading
import pytest
import arinna.mqtt_client


@pytest.fixture
def mqtt_client():
    mqtt_client = arinna.mqtt_client.MQTTClient()
    mqtt_client.connect()
    yield mqtt_client
    mqtt_client.disconnect()


@pytest.fixture
def mqtt_client_with_loop(mqtt_client):
    mqtt_client.loop_start()
    yield mqtt_client
    mqtt_client.loop_stop()


def test_mqtt_client_context_manager_support():
    with arinna.mqtt_client.MQTTClient() as mqtt_client:
        assert mqtt_client


def test_mqtt_client_stops_looping_when_disconnected():
    mqtt_client = arinna.mqtt_client.MQTTClient()
    mqtt_client.connect()
    t = threading.Thread(target=arinna.mqtt_client.MQTTClient.loop_forever,
                         args=(mqtt_client,))
    t.start()
    mqtt_client.disconnect()
    t.join(timeout=5)
    assert False is t.is_alive()


def test_mqtt_client_subscribes_to_topic(mqtt_client_with_loop):
    mutable_object = {'is_subscribed': False}

    def on_subscribe(_, user_data, *args):
        user_data['is_subscribed'] = True

    mqtt_client_with_loop.set_on_subscribe(on_subscribe)
    mqtt_client_with_loop.set_user_data(mutable_object)
    mqtt_client_with_loop.subscribe('sample_topic')

    async def wait_for_result(flag):
        while not flag['is_subscribed']:
            pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_for_result(mutable_object))
    loop.stop()

    assert True is mutable_object['is_subscribed']


def test_mqtt_client_receives_message_from_topic(mqtt_client_with_loop):
    mutable_object = {'message_received': False}

    def on_message(_, user_data, message):
        status = True if message.payload == b'True' else False
        user_data['message_received'] = status

    mqtt_client_with_loop.set_on_message(on_message)
    mqtt_client_with_loop.set_user_data(mutable_object)
    mqtt_client_with_loop.subscribe('sample_topic')
    mqtt_client_with_loop.publish('sample_topic', payload=True)

    async def wait_for_result(flag):
        while not flag['message_received']:
            pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_for_result(mutable_object))
    loop.stop()

    assert True is mutable_object['message_received']
