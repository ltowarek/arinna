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
    def __init__(self, mqtt_client=paho.mqtt.client.Client()):
        self.mqtt_client = mqtt_client
        self.subscriptions = {}

    def connect(self, host='localhost'):
        logger.info('Connecting MQTT client')
        self.mqtt_client.user_data_set(self.subscriptions)
        self.mqtt_client.on_message = on_message
        self.mqtt_client.connect(host)
        logger.info('MQTT client connected')

    def subscribe(self, topic, measurement, type_converter):
        logger.info('Subscribing to new topic')
        logger.info('Topic: {}'.format(topic))
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Type converter: {}'.format(type_converter))
        self.subscriptions[topic] = {
            'measurement': measurement,
            'type': type_converter
        }
        self.mqtt_client.subscribe(topic)
        logger.info('Subscribed to new topic')

    def disconnect(self):
        logger.info('Disconnecting MQTT client')
        self.mqtt_client.disconnect()
        logger.info('MQTT client disconnected')

    def loop(self):
        logger.debug('MQTT client loop')
        self.mqtt_client.loop()

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

    logger.info('MQTT loop started')
    try:
        with MQTTClient() as mqtt_client:
            mqtt_client.subscribe('inverter/response/grid_voltage',
                                  'grid_voltage',
                                  float)
            mqtt_client.subscribe('inverter/response/grid_frequency',
                                  'grid_frequency',
                                  float)
            mqtt_client.subscribe('inverter/response/ac_output_voltage',
                                  'ac_output_voltage', float)
            mqtt_client.subscribe('inverter/response/ac_output_frequency',
                                  'ac_output_frequency', float)
            mqtt_client.subscribe('inverter/response/ac_output_apparent_power',
                                  'ac_output_apparent_power', int)
            mqtt_client.subscribe('inverter/response/ac_output_active_power',
                                  'ac_output_active_power', int)
            mqtt_client.subscribe('inverter/response/output_load_percent',
                                  'output_load_percent', percent)
            mqtt_client.subscribe('inverter/response/bus_voltage',
                                  'bus_voltage', int)
            mqtt_client.subscribe('inverter/response/battery_voltage',
                                  'battery_voltage', float)
            mqtt_client.subscribe('inverter/response/battery_charging_current',
                                  'battery_charging_current', int)
            mqtt_client.subscribe('inverter/response/battery_capacity',
                                  'battery_capacity', percent)
            mqtt_client.subscribe(
                'inverter/response/inverter_heat_sink_temperature',
                'inverter_heat_sink_temperature', int)
            mqtt_client.subscribe(
                'inverter/response/pv_input_current_for_battery',
                'pv_input_current_for_battery', int)
            mqtt_client.subscribe('inverter/response/pv_input_voltage',
                                  'pv_input_voltage', float)
            mqtt_client.subscribe('inverter/response/battery_voltage_from_scc',
                                  'battery_voltage_from_scc', float)
            mqtt_client.subscribe(
                'inverter/response/battery_discharge_current',
                'battery_discharge_current', int)
            mqtt_client.subscribe(
                'inverter/response/is_sbu_priority_version_added',
                'is_sbu_priority_version_added', bool_from_string)
            mqtt_client.subscribe(
                'inverter/response/is_sbu_priority_version_added',
                'is_sbu_priority_version_added', bool_from_string)
            mqtt_client.subscribe('inverter/response/is_configuration_changed',
                                  'is_configuration_changed', bool_from_string)
            mqtt_client.subscribe('inverter/response/is_scc_firmware_updated',
                                  'is_scc_firmware_updated', bool_from_string)
            mqtt_client.subscribe('inverter/response/is_load_on', 'is_load_on',
                                  bool_from_string)
            mqtt_client.subscribe(
                'inverter/response/'
                'is_battery_voltage_to_steady_while_charging',
                'is_battery_voltage_to_steady_while_charging',
                bool_from_string)
            mqtt_client.subscribe('inverter/response/is_charging_on',
                                  'is_charging_on',
                                  bool_from_string)
            mqtt_client.subscribe('inverter/response/is_scc_charging_on',
                                  'is_scc_charging_on', bool_from_string)
            mqtt_client.subscribe('inverter/response/is_ac_charging_on',
                                  'is_ac_charging_on', bool_from_string)
            mqtt_client.subscribe(
                'inverter/response/battery_voltage_offset_for_fans_on',
                'battery_voltage_offset_for_fans_on', int)
            mqtt_client.subscribe('inverter/response/eeprom_version',
                                  'eeprom_version',
                                  int)
            mqtt_client.subscribe('inverter/response/pv_charging_power',
                                  'pv_charging_power', int)
            mqtt_client.subscribe(
                'inverter/response/is_charging_to_floating_enabled',
                'is_charging_to_floating_enabled', bool_from_string)
            mqtt_client.subscribe('inverter/response/is_switch_on',
                                  'is_switch_on',
                                  bool_from_string)
            mqtt_client.subscribe('inverter/response/is_dustproof_installed',
                                  'is_dustproof_installed', bool_from_string)

            mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info('MQTT loop stopped by user')
    except Exception:
        logger.exception('Unknown exception occurred')
    logger.info('MQTT loop stopped')

    return 0


if __name__ == '__main__':
    sys.exit(main())
