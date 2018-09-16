#!/usr/bin/env python3

import arinna.database_provider as db
import statistics
from tests.fakes.database import FakeDatabase
from tests.fakes.database import get_points_with_interval

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
    d = FakeDatabase()
    d.create_database(sample_database)
    yield d
    d.drop_database(sample_database)


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


def test_context_manager_support(database):
    database_client = db.DatabaseClient(database)
    with database_client as db_client:
        assert db_client
