#!/usr/bin/env python3

import arinna.database_provider as db
import statistics
import datetime
import re

import pytest


class FakeResultSet:
    def __init__(self, series):
        self.series = series

    def get_points(self, _):
        for s in self.series:
            yield s


class FakeDatabase:
    def __init__(self):
        self.measurements = {}

    def add_measurement(self, measurement):
        self.measurements[measurement] = []

    def add_values_to_measurement(self, values, measurement,
                                  interval=datetime.timedelta(seconds=1)):
        t = datetime.datetime.now() - len(values) * interval
        for v in values:
            self.add_value_to_measurement(v, measurement, t)
            t += interval

    def add_value_to_measurement(self, value, measurement, timestamp):
        self.measurements[measurement].append({
            'value': value,
            'time': timestamp
        })

    def query(self, query, database=None):
        m = re.match(r'SELECT (\w+)\("(\w+)"\) '
                     r'FROM "(\w+)" WHERE time > now\(\) - (\d+)(\w)', query)
        if not m:
            return None

        aggregation = m.group(1)
        field = m.group(2)
        measurement = m.group(3)
        value = int(m.group(4))
        unit = m.group(5)

        if unit == 's':
            timedelta = datetime.timedelta(seconds=value)
        elif unit == 'm':
            timedelta = datetime.timedelta(minutes=value)
        else:
            timedelta = datetime.timedelta()

        now = datetime.datetime.now()
        values = []
        for m in self.measurements[measurement]:
            if m['time'] > now - timedelta:
                values.append(m[field])

        if aggregation == 'MEAN':
            series = [{'mean': statistics.mean(values)}]
        elif aggregation == 'STDDEV':
            series = [{'stddev': statistics.stdev(values)}]
        else:
            series = [{}]

        return FakeResultSet(series)

    def write_points(self, points, database=None):
        pass

    def close(self):
        pass


@pytest.fixture
def sample_data():
    return [2, 5, 1, 6, 23]


@pytest.fixture
def sample_measurement():
    return 'sample_measurement'


@pytest.fixture
def fake_database(sample_data, sample_measurement):
    database = FakeDatabase()
    database.add_measurement(sample_measurement)
    database.add_values_to_measurement(sample_data, sample_measurement)
    return database


def test_moving_average_of_all_measurements(sample_data, sample_measurement,
                                            fake_database):
    database_client = db.DatabaseClient(fake_database)
    expected = statistics.mean(sample_data)
    actual = database_client.moving_average(sample_measurement,
                                            time_window='{}s'.format(
                                                len(sample_data) + 1))
    assert expected == actual


def test_moving_average_of_last_2_measurements(sample_data, sample_measurement,
                                               fake_database):
    database_client = db.DatabaseClient(fake_database)
    expected = statistics.mean(sample_data[-2:])
    actual = database_client.moving_average(sample_measurement,
                                            time_window='3s')
    assert expected == actual


def test_moving_stddev_of_all_measurements(sample_data, sample_measurement,
                                           fake_database):
    database_client = db.DatabaseClient(fake_database)
    expected = statistics.stdev(sample_data)
    actual = database_client.moving_stddev(sample_measurement,
                                           time_window='{}s'.format(
                                               len(sample_data) + 1))
    assert expected == actual


def test_moving_stddev_of_last_3_measurements(sample_data, sample_measurement,
                                              fake_database):
    database_client = db.DatabaseClient(fake_database)
    expected = statistics.stdev(sample_data[-3:])
    actual = database_client.moving_stddev(sample_measurement,
                                           time_window='4s')
    assert expected == actual
