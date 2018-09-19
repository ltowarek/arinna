#!/usr/bin/env python3

import arinna.inverter_provider as ip
import paho.mqtt.client
from tests.fakes.serial import FakeSerial


def test_on_message_sends_qpigs_to_inverter():
    fake_serial = FakeSerial()
    serial_adapter = ip.InverterSerialAdapter(fake_serial)
    message = paho.mqtt.client.MQTTMessage()

    ip.on_message(None, serial_adapter, message)

    assert fake_serial.last_written_data == ip.QPIGS


class MQTTSpy:
    def __init__(self):
        self._publish_messages = []

    @property
    def publish_messages(self):
        return self._publish_messages

    def publish(self, topic, payload):
        self._publish_messages.append({topic: payload})


def test_publish_responses_is_a_noop_given_no_responses_are_passed():
    mqtt_spy = MQTTSpy()
    responses = {}

    ip.publish_response(responses, mqtt_spy)

    assert mqtt_spy.publish_messages == []


def test_publish_responses_sends_responses_using_mqtt_client():
    mqtt_spy = MQTTSpy()
    responses = {
        'topic_a': 'value_a',
        'topic_b': 'value_b'
    }

    ip.publish_response(responses, mqtt_spy)

    expected_messages = [{'inverter/response/' + k: v} for k, v in
                         responses.items()]
    assert mqtt_spy.publish_messages == expected_messages


def test_serial_adapter_sends_qpigs_command():
    fake_serial = FakeSerial()
    command = ip.QPIGS
    serial_adapter = ip.InverterSerialAdapter(fake_serial)
    serial_adapter.send_command(command)
    assert command == fake_serial.last_written_data


def test_serial_adapter_receives_response_until_cr():
    fake_serial = FakeSerial()
    expected_response = b'sample_response'
    fake_serial.response = expected_response + b'\r'
    serial_adapter = ip.InverterSerialAdapter(fake_serial)
    actual_response = serial_adapter.receive_response()
    assert expected_response == actual_response


def test_serial_adapter_receives_two_responses_from_single_input():
    fake_serial = FakeSerial()
    expected_responses = [b'input1', b'input2']
    fake_serial.response = b'\r'.join(expected_responses) + b'\r'
    serial_adapter = ip.InverterSerialAdapter(fake_serial)
    for expected_response in expected_responses:
        actual_response = serial_adapter.receive_response()
        assert expected_response == actual_response


def test_is_valid_response_returns_false_given_ack_is_passed():
    assert ip.InverterSerialAdapter.is_valid_response(b'(ACK9 \r') is False


def test_is_valid_response_returns_false_given_nak_is_passed():
    assert ip.InverterSerialAdapter.is_valid_response(b'(NAKss\r') is False


def test_is_valid_response_returns_true_given_valid_response_is_passed():
    assert ip.InverterSerialAdapter.is_valid_response(b'(NAKss\r') is False


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
               '{end_byte}'.format(**self.tokens).encode()


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
