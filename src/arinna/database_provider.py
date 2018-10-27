#!/usr/bin/env python3

import logging
import arinna.log as log
import sys

from arinna.database_client import DatabaseClient
from arinna.mqtt_client import MQTTClient

logger = logging.getLogger(__name__)


def on_message(_, subscriptions, message):
    logger.info('Message received')
    logger.info('Payload: {}'.format(message.payload))
    logger.info('Topic: {}'.format(message.topic))
    topic = message.topic
    subscription = subscriptions[topic]
    raw_value = message.payload.decode().replace(',', '.')
    with DatabaseClient() as db_client:
        db_client.save(subscription['measurement'],
                       subscription['type'](raw_value))


def percent(value):
    return float(int(value) / 100)


def bool_from_string(value):
    return True if bool(int(value)) else False


def int_from_device_mode(value):
    mapping = {
        'Power On': 0,
        'Standby': 1,
        'Line': 2,
        'Battery': 3,
        'Fault': 4,
        'Power Saving': 5
    }
    return mapping[value]


def main():
    log.setup_logging()

    subscriptions = {
        'inverter/response/grid_voltage': {
            'measurement': 'grid_voltage',
            'type': float
        }, 'inverter/response/grid_frequency': {
            'measurement': 'grid_frequency',
            'type': float
        }, 'inverter/response/ac_output_voltage': {
            'measurement': 'ac_output_voltage',
            'type': float
        }, 'inverter/response/ac_output_frequency': {
            'measurement': 'ac_output_frequency',
            'type': float
        }, 'inverter/response/ac_output_apparent_power': {
            'measurement': 'ac_output_apparent_power',
            'type': int
        }, 'inverter/response/ac_output_active_power': {
            'measurement': 'ac_output_active_power',
            'type': int
        }, 'inverter/response/output_load_percent': {
            'measurement': 'output_load_percent',
            'type': percent
        }, 'inverter/response/bus_voltage': {
            'measurement': 'bus_voltage',
            'type': int
        }, 'inverter/response/battery_voltage': {
            'measurement': 'battery_voltage',
            'type': float
        }, 'inverter/response/battery_charging_current': {
            'measurement': 'battery_charging_current',
            'type': int
        }, 'inverter/response/battery_capacity': {
            'measurement': 'battery_capacity',
            'type': percent
        }, 'inverter/response/inverter_heat_sink_temperature': {
            'measurement': 'inverter_heat_sink_temperature',
            'type': int
        }, 'inverter/response/pv_input_current_for_battery': {
            'measurement': 'pv_input_current_for_battery',
            'type': int
        }, 'inverter/response/pv_input_voltage': {
            'measurement': 'pv_input_voltage',
            'type': float
        }, 'inverter/response/battery_voltage_from_scc': {
            'measurement': 'battery_voltage_from_scc',
            'type': float
        }, 'inverter/response/battery_discharge_current': {
            'measurement': 'battery_discharge_current',
            'type': int
        }, 'inverter/response/is_sbu_priority_version_added': {
            'measurement': 'is_sbu_priority_version_added',
            'type': bool_from_string
        }, 'inverter/response/is_configuration_changed': {
            'measurement': 'is_configuration_changed',
            'type': bool_from_string
        }, 'inverter/response/is_scc_firmware_updated': {
            'measurement': 'is_scc_firmware_updated',
            'type': bool_from_string
        }, 'inverter/response/is_load_on': {
            'measurement': 'is_load_on',
            'type': bool_from_string
        }, 'inverter/response/is_battery_voltage_to_steady_while_charging': {
            'measurement': 'is_battery_voltage_to_steady_while_charging',
            'type': bool_from_string
        }, 'inverter/response/is_charging_on': {
            'measurement': 'is_charging_on',
            'type': bool_from_string
        }, 'inverter/response/is_scc_charging_on': {
            'measurement': 'is_scc_charging_on',
            'type': bool_from_string
        }, 'inverter/response/is_ac_charging_on': {
            'measurement': 'is_ac_charging_on',
            'type': bool_from_string
        }, 'inverter/response/battery_voltage_offset_for_fans_on': {
            'measurement': 'battery_voltage_offset_for_fans_on',
            'type': int
        }, 'inverter/response/eeprom_version': {
            'measurement': 'eeprom_version',
            'type': int
        }, 'inverter/response/pv_charging_power': {
            'measurement': 'pv_charging_power',
            'type': int
        }, 'inverter/response/is_charging_to_floating_enabled': {
            'measurement': 'is_charging_to_floating_enabled',
            'type': bool_from_string
        }, 'inverter/response/is_switch_on': {
            'measurement': 'is_switch_on',
            'type': bool_from_string
        }, 'inverter/response/is_dustproof_installed': {
            'measurement': 'is_dustproof_installed',
            'type': bool_from_string
        }, 'inverter/response/device_mode': {
            'measurement': 'device_mode',
            'type': int_from_device_mode
        }
    }

    logger.info('MQTT loop started')
    try:
        with MQTTClient() as mqtt_client:
            mqtt_client.set_on_message(on_message)
            mqtt_client.set_user_data(subscriptions)
            for topic in subscriptions:
                mqtt_client.subscribe(topic)
            mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info('MQTT loop stopped by user')
    except Exception:
        logger.exception('Unknown exception occurred')
    logger.info('MQTT loop stopped')

    return 0


if __name__ == '__main__':
    sys.exit(main())
