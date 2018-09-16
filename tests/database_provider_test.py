#!/usr/bin/env python3

import arinna.database_provider as db
import statistics
from tests.fakes.database import FakeDatabase

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
def fake_database(sample_data, sample_measurement, sample_database):
    database = FakeDatabase()
    database.create_database(sample_database)
    yield database
    database.drop_database(sample_database)


def test_moving_average_without_measurements(sample_measurement,
                                             sample_database,
                                             fake_database):
    database_client = db.DatabaseClient(fake_database, db_name=sample_database)
    fake_database.add_measurement(sample_measurement)
    expected = None
    actual = database_client.moving_average(sample_measurement, '0s')
    assert expected == actual


def test_moving_average_of_all_measurements(sample_data, sample_measurement,
                                            sample_database,
                                            fake_database):
    fake_database.add_measurement(sample_measurement)
    fake_database.add_values_to_measurement(sample_data, sample_measurement)
    database_client = db.DatabaseClient(fake_database, db_name=sample_database)
    expected = statistics.mean(sample_data)
    actual = database_client.moving_average(sample_measurement,
                                            time_window='{}s'.format(
                                                len(sample_data) + 1))
    assert expected == actual


def test_moving_average_of_last_2_measurements(sample_data, sample_measurement,
                                               sample_database,
                                               fake_database):
    fake_database.add_measurement(sample_measurement)
    fake_database.add_values_to_measurement(sample_data, sample_measurement)
    database_client = db.DatabaseClient(fake_database, db_name=sample_database)
    expected = statistics.mean(sample_data[-2:])
    actual = database_client.moving_average(sample_measurement,
                                            time_window='3s')
    assert expected == actual


def test_moving_stddev_of_all_measurements(sample_data, sample_measurement,
                                           sample_database,
                                           fake_database):
    fake_database.add_measurement(sample_measurement)
    fake_database.add_values_to_measurement(sample_data, sample_measurement)
    database_client = db.DatabaseClient(fake_database, db_name=sample_database)
    expected = statistics.stdev(sample_data)
    actual = database_client.moving_stddev(sample_measurement,
                                           time_window='{}s'.format(
                                               len(sample_data) + 1))
    assert expected == actual


def test_moving_stddev_of_last_3_measurements(sample_data, sample_measurement,
                                              sample_database,
                                              fake_database):
    fake_database.add_measurement(sample_measurement)
    fake_database.add_values_to_measurement(sample_data, sample_measurement)
    database_client = db.DatabaseClient(fake_database, db_name=sample_database)
    expected = statistics.stdev(sample_data[-3:])
    actual = database_client.moving_stddev(sample_measurement,
                                           time_window='4s')
    assert expected == actual


def test_context_manager_support(fake_database):
    database_client = db.DatabaseClient(fake_database)
    with database_client as db_client:
        assert db_client
