#!/usr/bin/env python3

from collections import namedtuple
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
        raw_response = self.serial_adapter.getResponse(command)
        return raw_response

    @staticmethod
    def parse_response(raw_response):
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
            ResponseToken('is_battery_voltage_to_steady_while_charging', 87,
                          88),
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

        response = {}
        current_byte_id = 0
        current_token_id = 0
        current_token_value = ''

        logger.info('Parsing response')
        for c in raw_response:
            if c == '(':
                logger.debug('Resetting current byte and token ids')
                current_byte_id = 0
                current_token_id = 0
            else:
                if current_token_id < len(tokens) and \
                        current_byte_id == tokens[current_token_id].end:
                    logger.debug('Updating response')
                    key = tokens[current_token_id].name
                    value = current_token_value
                    logger.debug('Key: {}'.format(key))
                    logger.debug('Value: {}'.format(value))
                    response[key] = value
                    current_token_id += 1
                    logger.debug('Response updated')
                    logger.debug(
                        'Increasing token id to: {}'.format(current_token_id))
                if current_token_id < len(tokens) and \
                        current_byte_id == tokens[current_token_id].start:
                    logging.debug('Resetting current token value')
                    current_token_value = ''
                current_token_value = current_token_value + c
            current_byte_id += 1
        logger.info('Response parsed')

        logger.debug('Parsed response: {}'.format(response))
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
        for key, value in response.items():
            logger.info('Sending response')
            topic = 'inverter/response/' + key
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
            raw_response = serial_adapter.send_command(command)
            logger.info('Raw response: {}'.format(raw_response))
            response = serial_adapter.parse_response(raw_response)
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
