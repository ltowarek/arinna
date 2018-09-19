#!/usr/bin/env python3

import arinna.database_provider as db
import statistics
import threading
import influxdb
from tests.fakes.database import get_points_with_interval
import paho.mqtt.client

import pytest


@pytest.fixture
def sample_data():
    return [2, 5, 1, 6, 23]


@pytest.fixture
def sample_measurement():
    return 'sample_measurement'


@pytest.fixture
def sample_database():
    return 'sample_database'


@pytest.fixture
def database(sample_database):
    d = influxdb.InfluxDBClient()
    d.create_database(sample_database)
    yield d
    d.drop_database(sample_database)
    d.close()


@pytest.fixture
def database_with_data(database, sample_measurement, sample_data,
                       sample_database):
    points = get_points_with_interval(sample_data, sample_measurement)
    database.write_points(points, database=sample_database)
    return database


def test_moving_average_without_measurements(sample_measurement,
                                             sample_database,
                                             database):
    database_client = db.DatabaseClient(database, db_name=sample_database)
    expected = None
    actual = database_client.moving_average(sample_measurement, '0s')
    assert expected == actual


def test_moving_average_of_all_measurements(sample_data, sample_measurement,
                                            sample_database,
                                            database_with_data):
    database_client = db.DatabaseClient(database_with_data,
                                        db_name=sample_database)
    expected = statistics.mean(sample_data)
    actual = database_client.moving_average(sample_measurement,
                                            time_window='{}s'.format(
                                                len(sample_data) + 1))
    assert expected == actual


def test_moving_average_of_last_2_measurements(sample_data, sample_measurement,
                                               sample_database,
                                               database_with_data):
    database_client = db.DatabaseClient(database_with_data,
                                        db_name=sample_database)
    expected = statistics.mean(sample_data[-2:])
    actual = database_client.moving_average(sample_measurement,
                                            time_window='3s')
    assert expected == actual


def test_moving_stddev_of_all_measurements(sample_data, sample_measurement,
                                           sample_database,
                                           database_with_data):
    database_client = db.DatabaseClient(database_with_data,
                                        db_name=sample_database)
    expected = statistics.stdev(sample_data)
    actual = database_client.moving_stddev(sample_measurement,
                                           time_window='{}s'.format(
                                               len(sample_data) + 1))
    assert expected == actual


def test_moving_stddev_of_last_3_measurements(sample_data, sample_measurement,
                                              sample_database,
                                              database_with_data):
    database_client = db.DatabaseClient(database_with_data,
                                        db_name=sample_database)
    expected = statistics.stdev(sample_data[-3:])
    actual = database_client.moving_stddev(sample_measurement,
                                           time_window='4s')
    assert expected == actual


def test_database_client_context_manager_support(database):
    database_client = db.DatabaseClient(database)
    with database_client as db_client:
        assert db_client


def test_load(sample_data, sample_measurement,
              sample_database,
              database_with_data):
    database_client = db.DatabaseClient(database_with_data,
                                        db_name=sample_database)
    assert sample_data == database_client.load(sample_measurement,
                                               time_window='{}s'.format(
                                                   len(sample_data) + 1))


def test_save(database, sample_measurement):
    database_client = db.DatabaseClient(database)
    values = [1, 2]
    for v in values:
        database_client.save(sample_measurement, v)
    assert database_client.load(sample_measurement, '1s') == values


def test_bool_from_string_true():
    assert True is db.bool_from_string('1')


def test_bool_from_string_false():
    assert False is db.bool_from_string('0')


def test_percent():
    assert 0.00 == db.percent(0)
    assert 0.01 == db.percent(1)
    assert 0.02 == db.percent(2)
    assert 0.10 == db.percent(10)
    assert 0.20 == db.percent(20)
    assert 1.00 == db.percent(100)


@pytest.fixture
def mqtt_client():
    mqtt_client = db.MQTTClient(paho.mqtt.client.Client())
    mqtt_client.connect()
    yield mqtt_client
    mqtt_client.disconnect()


@pytest.fixture
def mqtt_client_with_loop(mqtt_client):
    mqtt_client.loop_start()
    yield mqtt_client
    mqtt_client.loop_stop()


def test_mqtt_client_context_manager_support():
    with db.MQTTClient(paho.mqtt.client.Client()) as mqtt_client:
        assert mqtt_client


def test_mqtt_client_stops_looping_when_disconnected():
    mqtt_client = db.MQTTClient(paho.mqtt.client.Client())
    mqtt_client.connect()
    t = threading.Thread(target=db.MQTTClient.loop_forever,
                         args=(mqtt_client,))
    t.start()
    mqtt_client.disconnect()
    t.join(timeout=5)
    assert False is t.is_alive()


def test_mqtt_client_subscribes_to_topic(mqtt_client_with_loop):
    mutable_object = {'is_subscribed': False}

    def on_subscribe(_, user_data, *args):
        user_data['is_subscribed'] = True

    mqtt_client_with_loop.set_on_subscribe(on_subscribe)
    mqtt_client_with_loop.set_user_data(mutable_object)
    mqtt_client_with_loop.subscribe('sample_topic')

    def wait_for_subscription(flag):
        while not flag['is_subscribed']:
            pass

    t = threading.Thread(target=wait_for_subscription,
                         args=(mutable_object,))
    t.start()
    t.join(timeout=5)

    assert True is mutable_object['is_subscribed']


def test_mqtt_client_receives_message_from_topic(mqtt_client_with_loop):
    mutable_object = {'message_received': False}

    def on_message(_, user_data, message):
        status = True if message.payload == b'True' else False
        user_data['message_received'] = status

    mqtt_client_with_loop.set_on_message(on_message)
    mqtt_client_with_loop.set_user_data(mutable_object)
    mqtt_client_with_loop.subscribe('sample_topic')
    mqtt_client_with_loop.publish('sample_topic', payload=True)

    def wait_for_message(flag):
        while not flag['message_received']:
            pass

    t = threading.Thread(target=wait_for_message,
                         args=(mutable_object,))
    t.start()
    t.join(timeout=5)

    assert True is mutable_object['message_received']
