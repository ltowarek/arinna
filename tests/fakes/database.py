#!/usr/bin/env python3

import statistics
import datetime
import re


class FakeResultSet:
    def __init__(self, series):
        self.series = series

    def get_points(self, _):
        for s in self.series:
            yield s


class FakeDatabase:
    def __init__(self):
        self.data = {}

    def query(self, query, database=None):
        now = datetime.datetime.utcnow()
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

        values = []
        for p in self.data[database]:
            if p['measurement'] == measurement and p['time'] > now - timedelta:
                values.append(p['fields'][field])

        series = []
        if values:
            if aggregation == 'MEAN':
                series = [{'mean': statistics.mean(values)}]
            elif aggregation == 'STDDEV':
                series = [{'stddev': statistics.stdev(values)}]

        return FakeResultSet(series)

    def write_points(self, points, database=None):
        self.data[database].extend(points)

    def close(self):
        pass

    def create_database(self, database):
        self.data[database] = []

    def drop_database(self, database):
        del self.data[database]


def get_points_with_interval(values, measurement,
                             interval=datetime.timedelta(seconds=1)):
    t = datetime.datetime.utcnow() - len(values) * interval
    points = []
    for v in values:
        point = {
            'measurement': measurement,
            'time': t,
            'fields': {
                'value': v,
            },
        }
        points.append(point)
        t += interval
    return points
