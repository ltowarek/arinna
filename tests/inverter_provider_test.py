#!/usr/bin/env python3

import arinna.inverter_provider as ip
import arinna.mqtt_client
import asyncio
import queue
import time


def test_mqtt_subscriber_puts_received_command_into_queue():
    command_queue = queue.Queue()
    command = 'QPIGS'
    with arinna.mqtt_client.MQTTClient() as mqtt_client:
        subscriber = ip.InverterMQTTSubscriber(command_queue, mqtt_client)
        subscriber.subscribe_request()
        mqtt_client.publish('inverter/request', command)
        time_end = time.time() + 60 * 5
        while time.time() < time_end and command_queue.empty():
            mqtt_client.loop()
    assert command == command_queue.get(timeout=5)


def test_mqtt_publisher_publishes_response():
    with arinna.mqtt_client.MQTTClient() as mqtt_client:
        def on_message(_, user_data, message):
            user_data['payload'] = message.payload.decode()
        mqtt_client.set_on_message(on_message)
        mutable_object = {'payload': None}
        mqtt_client.set_user_data(mutable_object)
        measurement = 'sample_measurement'
        mqtt_client.subscribe('inverter/response/' + measurement)

        response = {measurement: ['value', 'unit']}
        mqtt_adapter = ip.InverterMQTTPublisher(mqtt_client)
        mqtt_adapter.publish_response(response)

        async def wait_for_result(client, user_data):
            while not user_data['payload']:
                client.loop()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(wait_for_result(mqtt_client, mutable_object))
        loop.stop()

        assert response[measurement][0] == mutable_object['payload']


def test_mqtt_publisher_publishes_request():
    with arinna.mqtt_client.MQTTClient() as mqtt_client:
        def on_message(_, user_data, message):
            user_data['payload'] = message.payload.decode()
        mqtt_client.set_on_message(on_message)
        mutable_object = {'payload': None}
        mqtt_client.set_user_data(mutable_object)
        mqtt_client.subscribe('inverter/request')

        request = 'value'
        mqtt_adapter = ip.InverterMQTTPublisher(mqtt_client)
        mqtt_adapter.publish_request(request)

        async def wait_for_result(client, user_data):
            while not user_data['payload']:
                client.loop()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(wait_for_result(mqtt_client, mutable_object))
        loop.stop()

        assert request == mutable_object['payload']
