#!/usr/bin/env python3

import paho.mqtt.client
from collections import namedtuple
import logging
import logging.handlers
import os
import serial
import sys
import arinna.config as config


logger = logging.getLogger(__name__)


ResponseToken = namedtuple('ResponseToken', ['name', 'start', 'end'])


tokens = [
    ResponseToken('grid_voltage', 1, 6),
    ResponseToken('grid_frequency', 7, 11),
    ResponseToken('ac_output_voltage', 12, 17),
    ResponseToken('ac_output_frequency', 18, 22),
    ResponseToken('ac_output_apparent_power', 23, 27),
    ResponseToken('ac_output_active_power', 28, 32),
    ResponseToken('output_load_percent', 33, 36),
    ResponseToken('bus_voltage', 37, 40),
    ResponseToken('battery_voltage', 41, 46),
    ResponseToken('battery_charging_current', 47, 50),
    ResponseToken('battery_capacity', 51, 54),
    ResponseToken('inverter_heat_sink_temperature', 55, 59),
    ResponseToken('pv_input_current_for_battery', 60, 64),
    ResponseToken('pv_input_voltage', 65, 70),
    ResponseToken('battery_voltage_from_scc', 71, 76),
    ResponseToken('battery_discharge_current', 77, 82),
    ResponseToken('is_sbu_priority_version_added', 83, 84),
    ResponseToken('is_configuration_changed', 84, 85),
    ResponseToken('is_scc_firmware_updated', 85, 86),
    ResponseToken('is_load_on', 86, 87),
    ResponseToken('is_battery_voltage_to_steady_while_charging', 87, 88),
    ResponseToken('is_charging_on', 88, 89),
    ResponseToken('is_scc_charging_on', 89, 90),
    ResponseToken('is_ac_charging_on', 90, 91),
    ResponseToken('battery_voltage_offset_for_fans_on', 92, 94),
    ResponseToken('eeprom_version', 95, 97),
    ResponseToken('pv_charging_power', 98, 103),
    ResponseToken('is_charging_to_floating_enabled', 104, 105),
    ResponseToken('is_switch_on', 105, 106),
    ResponseToken('is_dustproof_installed', 106, 107)
]


def parse_response(raw_response):
    response = {}
    current_byte_id = 0
    current_token_id = 0
    current_token_value = ''

    logger.info('Parsing response')
    for b in raw_response:
        c = chr(b)
        if c == '(':
            logger.debug('Resetting current byte and token ids')
            current_byte_id = 0
            current_token_id = 0
        else:
            if current_token_id < len(tokens) and current_byte_id == tokens[current_token_id].end:
                logger.debug('Updating response')
                key = tokens[current_token_id].name
                value = current_token_value
                logger.debug('Key: {}'.format(key))
                logger.debug('Value: {}'.format(value))
                response[key] = value
                current_token_id += 1
                logger.debug('Response updated')
                logger.debug('Increasing token id to: {}'.format(current_token_id))
            if current_token_id < len(tokens) and current_byte_id == tokens[current_token_id].start:
                logging.debug('Resetting current token value')
                current_token_value = ''
            current_token_value = current_token_value + c
        current_byte_id += 1
    logger.info('Response parsed')

    return response


def publish_response(response, client):
    for key, value in response.items():
        logger.info('Sending response')
        topic = 'inverter/response/' + key
        logger.info('Topic: {}'.format(topic))
        logger.info('Payload: {}'.format(value))
        client.publish(topic, value)


def is_valid_response(response):
    return response != b'(ACK9 \r' and response != b'(NAKss\r'


def on_message(_, serial_port, message):
    logger.info('Message received')
    logger.info('Payload: {}'.format(message.payload))
    logger.info('Topic: {}'.format(message.topic))
    qpigs = bytes.fromhex('51 50 49 47 53 b7 a9 0d')
    with serial.Serial(serial_port, 2400) as s:
        s.write(qpigs)


def setup_logging(logs_directory):
    logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(logs_directory, 'inverter_provider.log'),
                                                             interval=5, when='m', backupCount=1)
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

    client = paho.mqtt.client.Client(userdata=settings.serial_port)
    client.on_message = on_message
    client.connect('localhost')
    client.subscribe('inverter/request')

    try:
        logger.info('Starting MQTT loop')
        client.loop_start()

        logger.info('Starting listening on port: {}'.format(settings.serial_port))
        while True:
            with serial.Serial(settings.serial_port, 2400) as s:
                raw_response = s.read_until(b'\r')
                logger.info('Raw response: {}'.format(raw_response))

                if not is_valid_response(raw_response):
                    logger.warning('Invalid response')
                    continue

                parsed_response = parse_response(raw_response)
                logger.debug('Parsed response: {}'.format(parsed_response))

                publish_response(parsed_response, client)
    except KeyboardInterrupt:
        logger.info('Listening loop stopped by user')
    except Exception as e:
        logger.exception('Unknown exception occurred', e)
    finally:
        client.loop_stop()
        client.disconnect()
    logger.info('Listening loop stopped')

    return 0


if __name__ == '__main__':
    sys.exit(main())
