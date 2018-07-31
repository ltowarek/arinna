#!/usr/bin/env python3

import paho.mqtt.client
import logging
import logging.handlers
import os
import sys
import arinna.config as config


logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self):
        self.mqtt_client = None
        
    def initialize(self, host='localhost'):
        logger.info('Initializing MQTT client')
        self.mqtt_client = paho.mqtt.client.Client()
        self.mqtt_client.connect(host)
        logger.info('MQTT client initialized')

    def close(self):
        logger.info('Disconnecting MQTT client')
        self.mqtt_client.disconnect()
        logger.info('MQTT client disconnected')

    def publish(self, topic, payload):
        logger.info('Publishing message')
        logger.info('Topic: {}'.format(topic))
        logger.info('Payload: {}'.format(payload))
        self.mqtt_client.publish(topic, payload)
        logger.info('Message published')


def setup_logging(logs_directory):
    logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.RotatingFileHandler(os.path.join(logs_directory, 'publisher.log'),
                                                        maxBytes=1000 * 1000, backupCount=1)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def main():
    settings = config.load()
    setup_logging(settings.logs_directory)

    publisher = Publisher()
    publisher.initialize()
    publisher.publish('inverter/request', 'QPIGS')
    publisher.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
