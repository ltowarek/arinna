#!/usr/bin/env python3

import paho.mqtt.client
import logging

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self, mqtt_client=None):
        if not mqtt_client:
            self.mqtt_client = paho.mqtt.client.Client()
            self.mqtt_client.enable_logger()
        else:
            self.mqtt_client = mqtt_client

    def connect(self, host='localhost'):
        logger.info('Connecting MQTT client')
        logger.info('Host: {}'.format(host))
        self.mqtt_client.connect(host)
        logger.info('MQTT client connected')

    def set_on_message(self, callback):
        logger.info('Setting on_message callback')
        logger.info('Callback: {}'.format(callback))
        self.mqtt_client.on_message = callback
        logger.info('on_message callback set')

    def set_on_subscribe(self, callback):
        logger.info('Setting on_subscribe callback')
        logger.info('Callback: {}'.format(callback))
        self.mqtt_client.on_subscribe = callback
        logger.info('on_subscribe callback set')

    def set_user_data(self, data):
        logger.info('Setting user data')
        logger.info('Data: {}'.format(data))
        self.mqtt_client.user_data_set(data)
        logger.info('User data set')

    def subscribe(self, topic):
        logger.info('Subscribing to new topic')
        logger.info('Topic: {}'.format(topic))
        self.mqtt_client.subscribe(topic)
        logger.info('Subscribed to new topic')

    def publish(self, topic, payload=None):
        logger.info('Publishing message')
        logger.info('Topic: {}'.format(topic))
        logger.info('Payload: {}'.format(payload))
        self.mqtt_client.publish(topic, payload=payload)
        logger.info('Message published')

    def disconnect(self):
        logger.info('Disconnecting MQTT client')
        self.mqtt_client.disconnect()
        logger.info('MQTT client disconnected')

    def loop(self):
        logger.debug('Looping MQTT client once')
        self.mqtt_client.loop()

    def loop_start(self):
        logger.debug('Starting MQTT client loop')
        self.mqtt_client.loop_start()
        logger.debug('MQTT client loop started')

    def loop_stop(self):
        logger.debug('Stopping MQTT client loop')
        self.mqtt_client.loop_stop()
        logger.debug('MQTT client loop stopped')

    def loop_forever(self):
        logger.debug('Starting infinite MQTT client loop')
        self.mqtt_client.loop_forever()

    def __enter__(self):
        logger.debug('Entering context manager')
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug('Exiting context manager')
        self.disconnect()
