#!/usr/bin/env python3

import influxdb
import paho.mqtt.client
import logging
import logging.handlers
import os
import sys
import arinna.config as config

logger = logging.getLogger(__name__)


class DatabaseClient:
    def __init__(self, db_client=influxdb.InfluxDBClient(),
                 db_name='inverter'):
        self.db_client = db_client
        self.db_name = db_name

    def close(self):
        logger.info('Closing database connection')
        self.db_client.close()
        logger.info('Database connection closed')

    def save(self, measurement, value):
        logger.info('Saving points into database')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Value: {}'.format(value))
        self.db_client.write_points([{
            'measurement': measurement,
            'fields': {
                'value': value
            }
        }], database=self.db_name)
        logger.info('Points saved into database')

    def load(self, measurement, time_window):
        logger.info('Loading points from database')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT "value" ' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Points load from database')
        return [point['value'] for point in result.get_points(measurement)]

    def moving_average(self, measurement, time_window):
        logger.info('Getting moving average')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT MEAN("value") ' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Moving average get')
        for point in result.get_points(measurement):
            return point['mean']
        return None

    def moving_stddev(self, measurement, time_window):
        logger.info('Getting moving stddev')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT STDDEV("value") ' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Moving stddev get')
        return next(result.get_points(measurement))['stddev']

    def __enter__(self):
        logger.debug('Entering context manager')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug('Exiting context manager')
        self.close()


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


class MQTTClient:
    def __init__(self, mqtt_client=None):
        if not mqtt_client:
            self.mqtt_client = paho.mqtt.client.Client()
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


def setup_logging(logs_directory):
    logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(logs_directory, 'database_provider.log'),
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


def percent(value):
    return float(int(value) / 100)


def bool_from_string(value):
    return True if bool(int(value)) else False


def main():
    settings = config.load()
    setup_logging(settings.logs_directory)

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
            'type': bool_from_string
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
        }
    }

    logger.info('MQTT loop started')
    try:
        with MQTTClient() as mqtt_client:
            mqtt_client.set_on_message(on_message)
            mqtt_client.set_user_data(subscriptions)
            mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info('MQTT loop stopped by user')
    except Exception:
        logger.exception('Unknown exception occurred')
    logger.info('MQTT loop stopped')

    return 0


if __name__ == '__main__':
    sys.exit(main())
