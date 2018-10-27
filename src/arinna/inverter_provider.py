#!/usr/bin/env python3

import logging
import arinna.log as log
import sys
import queue
import arinna.config as config
import arinna.mqtt_client
import mppsolar

logger = logging.getLogger(__name__)


class InverterSerialAdapter:
    def __init__(self, port, baudrate=2400):
        logger.info('Port: {}'.format(port))
        logger.info('Baudrate: {}'.format(baudrate))
        self.serial_adapter = mppsolar.mppUtils(port, baudrate)

    def send_command(self, command):
        response = self.serial_adapter.getResponseDict(command)
        return response


def on_message(_, command_queue, message):
    logger.info('Message received')
    logger.info('Payload: {}'.format(message.payload))
    logger.info('Topic: {}'.format(message.topic))
    command_queue.put(message.payload.decode())


class InverterMQTTSubscriber:
    def __init__(self, command_queue, mqtt_client):
        self.command_queue = command_queue
        self.mqtt_client = mqtt_client

    def subscribe_request(self):
        self.mqtt_client.set_user_data(self.command_queue)
        self.mqtt_client.set_on_message(on_message)
        self.mqtt_client.subscribe('inverter/request')


class InverterMQTTPublisher:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def publish_response(self, response):
        for key, status in response.items():
            logger.info('Sending response')
            topic = 'inverter/response/' + key
            value, unit = status
            logger.info('Topic: {}'.format(topic))
            logger.info('Payload: {}'.format(value))
            self.mqtt_client.publish(topic, value)

    def publish_request(self, request):
        logger.info('Publishing message')
        topic = 'inverter/request'
        logger.info('Topic: {}'.format(topic))
        logger.info('Payload: {}'.format(request))
        self.mqtt_client.publish(topic, request)
        logger.info('Message published')


def main():
    settings = config.load()
    log.setup_logging()

    serial_adapter = InverterSerialAdapter(settings.serial_port)
    command_queue = queue.Queue()

    logger.info('Starting MQTT loop')
    mqtt_client = arinna.mqtt_client.MQTTClient()
    mqtt_client.connect()
    mqtt_client.loop_start()
    mqtt_subscriber = InverterMQTTSubscriber(command_queue,
                                             mqtt_client)
    mqtt_subscriber.subscribe_request()
    mqtt_publisher = InverterMQTTPublisher(mqtt_client)

    try:
        logger.info('Starting listening loop')
        while True:
            logger.info('Waiting for command')
            command = command_queue.get()
            logger.info('Command received: {}'.format(command))
            response = serial_adapter.send_command(command)
            logger.info('Response: {}'.format(response))
            mqtt_publisher.publish_response(response)
    except KeyboardInterrupt:
        logger.info('Listening loop stopped by user')
    except Exception:
        logger.exception('Unknown exception occurred')
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    logger.info('Listening loop stopped')

    return 0


if __name__ == '__main__':
    sys.exit(main())
