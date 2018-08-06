#!/usr/bin/env python3

import arinna.inverter_provider as ip
import paho.mqtt.client
import io


def test_is_valid_response_returns_false_given_ack_is_passed():
    assert ip.is_valid_response(b'(ACK9 \r') is False


def test_is_valid_response_returns_false_given_nak_is_passed():
    assert ip.is_valid_response(b'(NAKss\r') is False


def test_is_valid_response_returns_true_given_valid_response_is_passed():
    assert ip.is_valid_response(b'(NAKss\r') is False


class SerialSpy(io.RawIOBase):
    def __init__(self):
        super().__init__()
        self._write_message = None

    @property
    def write_message(self):
        return self._write_message

    def write(self, message):
        self._write_message = message


def test_on_message_sends_qpigs_to_inverter():
    serial_spy = SerialSpy()
    message = paho.mqtt.client.MQTTMessage()

    ip.on_message(None, serial_spy, message)

    assert serial_spy.write_message == ip.qpigs


class MQTTSpy:
    def __init__(self):
        self._publish_messages = []

    @property
    def publish_messages(self):
        return self._publish_messages

    def publish(self, topic, payload):
        self._publish_messages.append({topic: payload})


def test_publish_responses_is_a_noop_given_no_responses_are_passed():
    mqtt_spy = MQTTSpy()
    responses = {}

    ip.publish_response(responses, mqtt_spy)

    assert mqtt_spy.publish_messages == []


def test_publish_responses_sends_responses_using_mqtt_client():
    mqtt_spy = MQTTSpy()
    responses = {
        'topic_a': 'value_a',
        'topic_b': 'value_b'
    }

    ip.publish_response(responses, mqtt_spy)

    expected_messages = [{'inverter/response/' + k: v} for k, v in
                         responses.items()]
    assert mqtt_spy.publish_messages == expected_messages
