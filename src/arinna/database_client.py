#!/usr/bin/env python3

import influxdb
import logging

logger = logging.getLogger(__name__)


class DatabaseClient:
    def __init__(self, db_client=None,
                 db_name='inverter'):
        if not db_client:
            self.db_client = influxdb.InfluxDBClient()
        else:
            self.db_client = db_client
        self.db_name = db_name

    def close(self):
        logger.info('Closing database connection')
        self.db_client.close()
        logger.info('Database connection closed')

    def save(self, measurement, value):
        logger.info('Saving points into database')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Value: {}'.format(value))
        self.db_client.write_points([{
            'measurement': measurement,
            'fields': {
                'value': value
            }
        }], database=self.db_name)
        logger.info('Points saved into database')

    def load(self, measurement, time_window):
        logger.info('Loading points from database')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT "value" ' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Points load from database')
        return [point['value'] for point in result.get_points(measurement)]

    def moving_average(self, measurement, time_window):
        logger.info('Getting moving average')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT MEAN("value") ' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Moving average get')
        for point in result.get_points(measurement):
            return point['mean']
        else:
            raise RuntimeError(
                'No moving average available for measurement \"{}\"'
                ' and time window \"{}\"'.format(measurement, time_window))

    def moving_stddev(self, measurement, time_window):
        logger.info('Getting moving stddev')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT STDDEV("value") ' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Moving stddev get')
        for point in result.get_points(measurement):
            return point['stddev']
        else:
            raise RuntimeError(
                'No moving stddev available for measurement \"{}\"'
                ' and time window \"{}\"'.format(measurement, time_window))

    def moving_min(self, measurement, time_window):
        logger.info('Getting moving min')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT MIN("value") ' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Moving min get')
        for point in result.get_points(measurement):
            return point['min']
        else:
            raise RuntimeError(
                'No moving min available for measurement \"{}\"'
                ' and time window \"{}\"'.format(measurement, time_window))

    def moving_max(self, measurement, time_window):
        logger.info('Getting moving max')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT MAX("value") ' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Moving max get')
        for point in result.get_points(measurement):
            return point['max']
        else:
            raise RuntimeError(
                'No moving max available for measurement \"{}\"'
                ' and time window \"{}\"'.format(measurement, time_window))

    def moving_true_percentage(self, measurement, time_window):
        logger.info('Getting moving true percentage')
        logger.info('Measurement: {}'.format(measurement))
        logger.info('Time window: {}'.format(time_window))
        query = 'SELECT "value"' \
                'FROM "{}" WHERE time > now() - {}'.format(measurement,
                                                           time_window)
        logger.debug('Query: {}'.format(query))
        result = self.db_client.query(query, database=self.db_name)
        logger.debug('Query result: {}'.format(result))
        logger.info('Moving true percentage get')
        values = [p['value'] for p in result.get_points(measurement)]
        if not values:
            raise RuntimeError(
                'No moving true percentage available for measurement \"{}\"'
                ' and time window \"{}\"'.format(measurement, time_window))
        return true_percentage(values)

    def __enter__(self):
        logger.debug('Entering context manager')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug('Exiting context manager')
        self.close()


def true_percentage(x):
    return len([y for y in x if y is True]) / len(x)
