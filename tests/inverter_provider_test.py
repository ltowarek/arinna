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
