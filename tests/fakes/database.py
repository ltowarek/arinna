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
