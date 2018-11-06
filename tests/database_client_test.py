#!/usr/bin/env python3

import statistics
import influxdb
import pytest
from arinna.database_client import DatabaseClient
from tests.fakes.database import get_points_with_interval


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


def database_default_constructor():
    database_client = DatabaseClient()
    assert database_client.db_client is not None
    assert 'inverter' == database_client.db_name


def test_moving_average_without_measurements(sample_measurement,
                                             sample_database,
                                             database):
    database_client = DatabaseClient(database, db_name=sample_database)
    with pytest.raises(RuntimeError):
        database_client.moving_average(sample_measurement, '1m')


def test_moving_average_of_all_measurements(sample_data, sample_measurement,
                                            sample_database,
                                            database_with_data):
    database_client = DatabaseClient(database_with_data,
                                     db_name=sample_database)
    expected = statistics.mean(sample_data)
    actual = database_client.moving_average(sample_measurement,
                                            time_window='{}s'.format(
                                                len(sample_data) + 1))
    assert expected == actual


def test_moving_average_of_last_2_measurements(sample_data, sample_measurement,
                                               sample_database,
                                               database_with_data):
    database_client = DatabaseClient(database_with_data,
                                     db_name=sample_database)
    expected = statistics.mean(sample_data[-2:])
    actual = database_client.moving_average(sample_measurement,
                                            time_window='3s')
    assert expected == actual


def test_moving_stddev_without_measurements(sample_measurement,
                                            sample_database,
                                            database):
    database_client = DatabaseClient(database,
                                     db_name=sample_database)
    with pytest.raises(RuntimeError):
        database_client.moving_stddev(sample_measurement,
                                      time_window='0s')


def test_moving_stddev_of_all_measurements(sample_data, sample_measurement,
                                           sample_database,
                                           database_with_data):
    database_client = DatabaseClient(database_with_data,
                                     db_name=sample_database)
    expected = statistics.stdev(sample_data)
    actual = database_client.moving_stddev(sample_measurement,
                                           time_window='{}s'.format(
                                               len(sample_data) + 1))
    assert expected == actual


def test_moving_stddev_of_last_3_measurements(sample_data, sample_measurement,
                                              sample_database,
                                              database_with_data):
    database_client = DatabaseClient(database_with_data,
                                     db_name=sample_database)
    expected = statistics.stdev(sample_data[-3:])
    actual = database_client.moving_stddev(sample_measurement,
                                           time_window='4s')
    assert expected == actual


def test_database_client_context_manager_support(database):
    database_client = DatabaseClient(database)
    with database_client as db_client:
        assert db_client


def test_load(sample_data, sample_measurement,
              sample_database,
              database_with_data):
    database_client = DatabaseClient(database_with_data,
                                     db_name=sample_database)
    assert sample_data == database_client.load(sample_measurement,
                                               time_window='{}s'.format(
                                                   len(sample_data) + 1))


def test_save(database, sample_measurement):
    database_client = DatabaseClient(database)
    values = [1, 2]
    for v in values:
        database_client.save(sample_measurement, v)
    assert database_client.load(sample_measurement, '1s') == values
