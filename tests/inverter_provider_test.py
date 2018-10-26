#!/usr/bin/env python3

import arinna.inverter_provider as ip
import arinna.mqtt_client
import asyncio
import queue
import time


def test_mqtt_subscriber_puts_received_command_into_queue():
    command_queue = queue.Queue()
    command = 'QPIGS'
    with arinna.mqtt_client.MQTTClient() as mqtt_client:
        subscriber = ip.InverterMQTTSubscriber(command_queue, mqtt_client)
        subscriber.subscribe_request()
        mqtt_client.publish('inverter/request', command)
        time_end = time.time() + 60 * 5
        while time.time() < time_end and command_queue.empty():
            mqtt_client.loop()
    assert command == command_queue.get(timeout=5)


def test_mqtt_publisher_publishes_response():
    with arinna.mqtt_client.MQTTClient() as mqtt_client:
        def on_message(_, user_data, message):
            user_data['payload'] = message.payload.decode()
        mqtt_client.set_on_message(on_message)
        mutable_object = {'payload': None}
        mqtt_client.set_user_data(mutable_object)
        measurement = 'sample_measurement'
        mqtt_client.subscribe('inverter/response/' + measurement)

        response = {measurement: 'value'}
        mqtt_adapter = ip.InverterMQTTPublisher(mqtt_client)
        mqtt_adapter.publish_response(response)

        async def wait_for_result(client, user_data):
            while not user_data['payload']:
                client.loop()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(wait_for_result(mqtt_client, mutable_object))
        loop.stop()

        assert response[measurement] == mutable_object['payload']


def test_mqtt_publisher_publishes_request():
    with arinna.mqtt_client.MQTTClient() as mqtt_client:
        def on_message(_, user_data, message):
            user_data['payload'] = message.payload.decode()
        mqtt_client.set_on_message(on_message)
        mutable_object = {'payload': None}
        mqtt_client.set_user_data(mutable_object)
        mqtt_client.subscribe('inverter/request')

        request = 'value'
        mqtt_adapter = ip.InverterMQTTPublisher(mqtt_client)
        mqtt_adapter.publish_request(request)

        async def wait_for_result(client, user_data):
            while not user_data['payload']:
                client.loop()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(wait_for_result(mqtt_client, mutable_object))
        loop.stop()

        assert request == mutable_object['payload']


class QPIGSResponseBuilder:
    def __init__(self):
        self.tokens = {
            'start_byte': '(',
            'grid_voltage': '000.0',
            'grid_frequency': '00.0',
            'ac_output_voltage': '000.0',
            'ac_output_frequency': '00.0',
            'ac_output_apparent_power': '0000',
            'ac_output_active_power': '0000',
            'output_load_percent': '000',
            'bus_voltage': '000',
            'battery_voltage': '00.00',
            'battery_charging_current': '000',
            'battery_capacity': '000',
            'inverter_heat_sink_temperature': '0000',
            'pv_input_current_for_battery': '0000',
            'pv_input_voltage': '000.0',
            'battery_voltage_from_scc': '00.00',
            'battery_discharge_current': '00000',
            'is_sbu_priority_version_added': '0',
            'is_configuration_changed': '0',
            'is_scc_firmware_updated': '0',
            'is_load_on': '0',
            'is_battery_voltage_to_steady_while_charging': '0',
            'is_charging_on': '0',
            'is_scc_charging_on': '0',
            'is_ac_charging_on': '0',
            'battery_voltage_offset_for_fans_on': '00',
            'eeprom_version': '00',
            'pv_charging_power': '00000',
            'is_charging_to_floating_enabled': '0',
            'is_switch_on': '0',
            'is_dustproof_installed': '0',
            'crc': '00',
            'end_byte': '\r'
        }

    def set_tokens(self, **kwargs):
        for key, value in kwargs.items():
            self.tokens[key] = value

    def prepare_response(self):
        return '{start_byte}' \
               '{grid_voltage} ' \
               '{grid_frequency} ' \
               '{ac_output_voltage} ' \
               '{ac_output_frequency} ' \
               '{ac_output_apparent_power} ' \
               '{ac_output_active_power} ' \
               '{output_load_percent} ' \
               '{bus_voltage} ' \
               '{battery_voltage} ' \
               '{battery_charging_current} ' \
               '{battery_capacity} ' \
               '{inverter_heat_sink_temperature} ' \
               '{pv_input_current_for_battery} ' \
               '{pv_input_voltage} ' \
               '{battery_voltage_from_scc} ' \
               '{battery_discharge_current} ' \
               '{is_sbu_priority_version_added}' \
               '{is_configuration_changed}' \
               '{is_scc_firmware_updated}' \
               '{is_load_on}' \
               '{is_battery_voltage_to_steady_while_charging}' \
               '{is_charging_on}' \
               '{is_scc_charging_on}' \
               '{is_ac_charging_on} ' \
               '{battery_voltage_offset_for_fans_on} ' \
               '{eeprom_version} ' \
               '{pv_charging_power} ' \
               '{is_charging_to_floating_enabled}' \
               '{is_switch_on}' \
               '{is_dustproof_installed}' \
               '{crc}' \
               '{end_byte}'.format(**self.tokens)


def verify_parsed_response(key, value):
    builder = QPIGSResponseBuilder()
    builder.set_tokens(**{key: value})
    raw_response = builder.prepare_response()
    parsed_response = ip.InverterSerialAdapter.parse_response(raw_response)
    assert value == parsed_response[key]


def test_parse_response_grid_voltage():
    verify_parsed_response('grid_voltage', '123.4')


def test_parse_response_grid_frequency():
    verify_parsed_response('grid_frequency', '12.3')


def test_parse_response_ac_output_voltage():
    verify_parsed_response('ac_output_voltage', '123.4')


def test_parse_response_ac_output_frequency():
    verify_parsed_response('ac_output_frequency', '12.3')


def test_parse_response_ac_output_apparent_power():
    verify_parsed_response('ac_output_apparent_power', '1234')


def test_parse_response_ac_output_active_power():
    verify_parsed_response('ac_output_active_power', '1234')


def test_parse_response_output_load_percent():
    verify_parsed_response('output_load_percent', '123')


def test_parse_response_bus_voltage():
    verify_parsed_response('bus_voltage', '123')


def test_parse_response_battery_voltage():
    verify_parsed_response('battery_voltage', '12.34')


def test_parse_response_battery_charging_current():
    verify_parsed_response('battery_charging_current', '123')


def test_parse_response_battery_capacity():
    verify_parsed_response('battery_capacity', '123')


def test_parse_response_inverter_heat_sink_temperature():
    verify_parsed_response('inverter_heat_sink_temperature', '1234')


def test_parse_response_pv_input_current_for_battery():
    verify_parsed_response('pv_input_current_for_battery', '1234')


def test_parse_response_pv_input_voltage():
    verify_parsed_response('pv_input_voltage', '123.4')


def test_parse_response_battery_voltage_from_scc():
    verify_parsed_response('battery_voltage_from_scc', '12.34')


def test_parse_response_battery_discharge_current():
    verify_parsed_response('battery_discharge_current', '12345')


def test_parse_response_is_sbu_priority_version_added():
    verify_parsed_response('is_sbu_priority_version_added', '1')


def test_parse_response_is_configuration_changed():
    verify_parsed_response('is_configuration_changed', '1')


def test_parse_response_is_scc_firmware_updated():
    verify_parsed_response('is_scc_firmware_updated', '1')


def test_parse_response_is_load_on():
    verify_parsed_response('is_load_on', '1')


def test_parse_response_is_battery_voltage_to_steady_while_charging():
    verify_parsed_response('is_battery_voltage_to_steady_while_charging', '1')


def test_parse_response_is_charging_on():
    verify_parsed_response('is_charging_on', '1')


def test_parse_response_is_scc_charging_on():
    verify_parsed_response('is_scc_charging_on', '1')


def test_parse_response_is_ac_charging_on():
    verify_parsed_response('is_ac_charging_on', '1')


def test_parse_response_battery_voltage_offset_for_fans_on():
    verify_parsed_response('battery_voltage_offset_for_fans_on', '12')


def test_parse_response_eeprom_version():
    verify_parsed_response('eeprom_version', '12')


def test_parse_response_pv_charging_power():
    verify_parsed_response('pv_charging_power', '12345')


def test_parse_response_is_charging_to_floating_enabled():
    verify_parsed_response('is_charging_to_floating_enabled', '1')


def test_parse_response_is_switch_on():
    verify_parsed_response('is_switch_on', '1')


def test_parse_response_is_dustproof_installed():
    verify_parsed_response('is_dustproof_installed', '1')
