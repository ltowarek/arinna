#!/usr/bin/env python3

import influxdb
import pytest
from tests.fakes.database import FakeDatabase
from tests.fakes.database import get_points_with_interval


@pytest.fixture
def sample_measurement():
    return 'sample_measurement'


@pytest.fixture
def sample_database():
    return 'sample_database'


@pytest.fixture(params=[influxdb.InfluxDBClient, FakeDatabase])
def implementation(request, sample_measurement, sample_database):
    database = request.param()
    database.create_database(sample_database)
    database.write_points(get_points_with_interval([1], sample_measurement),
                          database=sample_database)
    yield database
    database.drop_database(sample_database)


def test_query_mean_without_values(sample_measurement,
                                   sample_database,
                                   implementation):
    query = 'SELECT MEAN("value") ' \
            'FROM "{}" WHERE time > now() - {}'.format(sample_measurement,
                                                       '0s')

    result = implementation.query(query, database=sample_database)

    with pytest.raises(StopIteration):
        next(result.get_points(sample_measurement))
