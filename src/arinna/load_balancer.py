#!/usr/bin/env python3

import paho.mqtt.client
import logging
import logging.handlers
import os
import sys
import arinna.config as config

logger = logging.getLogger(__name__)


def can_add_load(battery_voltage, pv_voltage_stddev):
    if not battery_voltage or not pv_voltage_stddev:
        return False
    if is_battery_fully_charged(battery_voltage) and \
            is_maximum_power_point_reached(pv_voltage_stddev):
        return True
    return False


def is_battery_fully_charged(voltage):
    return voltage >= 56.0


def is_maximum_power_point_reached(voltage_stddev):
    return voltage_stddev < 1.0


def on_message(_, __, message):
    logger.info('Message received')
    logger.info('Payload: {}'.format(message.payload))
    logger.info('Topic: {}'.format(message.topic))


def setup_logging(logs_directory):
    logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(logs_directory, 'load_balancer.log'),
        interval=5, when='m', backupCount=1)
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

    client = paho.mqtt.client.Client()
    client.on_message = on_message
    client.connect('localhost')
    client.subscribe('inverter/request')

    try:
        logger.info('Starting MQTT loop')
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info('Listening loop stopped by user')
    except Exception as e:
        logger.exception('Unknown exception occurred')
    finally:
        client.disconnect()
    logger.info('Listening loop stopped')

    return 0


if __name__ == '__main__':
    sys.exit(main())
