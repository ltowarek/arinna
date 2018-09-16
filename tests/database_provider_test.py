#!/usr/bin/env python3

import arinna.database_provider as db
import statistics
import datetime
import re
import influxdb

import pytest


class FakeResultSet:
    def __init__(self, series):
        self.series = series

    def get_points(self, _):
        for s in self.series:
            yield s


class FakeDatabase:
    def __init__(self):
        self.databases = {}
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

        series = []
        if values:
            if aggregation == 'MEAN':
                series = [{'mean': statistics.mean(values)}]
            elif aggregation == 'STDDEV':
                series = [{'stddev': statistics.stdev(values)}]

        return FakeResultSet(series)

    def write_points(self, points, database=None):
        for point in points:
            name = point['measurement']
            measurement = {}
            for key, value in point['fields'].items():
                measurement[key] = value
            if 'time' not in measurement:
                measurement['time'] = datetime.datetime.now()
            self.measurements.setdefault(name, []).append(measurement)

    def close(self):
        pass

    def create_database(self, database):
        self.databases[database] = {}

    def drop_database(self, database):
        del self.databases[database]


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


@pytest.fixture(params=[influxdb.InfluxDBClient, FakeDatabase])
def database_implementation(request, sample_database):
    database = request.param()
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


def test_database_contract_query_mean_without_values(sample_measurement,
                                                     sample_database,
                                                     database_implementation):
    database_implementation.write_points([{
        'measurement': sample_measurement,
        'fields': {
            'value': 1
        }
    }], database=sample_database)
    query = 'SELECT MEAN("value") ' \
            'FROM "{}" WHERE time > now() - {}'.format(sample_measurement,
                                                       '0s')

    result = database_implementation.query(query, database=sample_database)

    with pytest.raises(StopIteration):
        next(result.get_points(sample_measurement))
