#!/usr/bin/env python3

import arinna.database_provider as db
import statistics
import time
import pytest


@pytest.fixture
def database_client():
    database = 'test_database'
    client = db.DatabaseClient(database)
    client.initialize()
    yield client
    client.drop_database()
    client.close()


def populate_measurement_with_1s_delay(database, measurement, values):
    for v in values:
        database.save(measurement, v)
        time.sleep(1)


def test_moving_average_of_all_measurements(database_client):
    measurement = 'test_measurement'
    values = range(1, 4)
    populate_measurement_with_1s_delay(database_client, measurement, values)

    expected = statistics.mean(values)
    actual = database_client.moving_average(measurement,
                                            time_window=len(values) + 1)
    assert expected == actual


def test_moving_average_of_last_2_measurements(database_client):
    measurement = 'test_measurement'
    values = range(1, 4)
    populate_measurement_with_1s_delay(database_client, measurement, values)

    expected = statistics.mean(values[-2:])
    actual = database_client.moving_average(measurement, time_window=3)
    assert expected == actual
