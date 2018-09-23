#!/usr/bin/env python3

import arinna.inverter_provider as inverter_provider
import logging
import logging.handlers
import os
import sys
import arinna.config as config
import arinna.database_provider as database_provider
import paho.mqtt.client

logger = logging.getLogger(__name__)


def setup_logging(logs_directory):
    logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(logs_directory, 'publisher.log'),
        maxBytes=1000 * 1000, backupCount=1)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def main():
    settings = config.load()
    setup_logging(settings.logs_directory)

    with database_provider.MQTTClient(
            paho.mqtt.client.Client()) as mqtt_client:
        publisher = inverter_provider.InverterMQTTPublisher(mqtt_client)
        publisher.publish_request('QPIGS')

    return 0


if __name__ == '__main__':
    sys.exit(main())
