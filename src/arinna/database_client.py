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
        return None

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
        return next(result.get_points(measurement))['stddev']

    def __enter__(self):
        logger.debug('Entering context manager')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug('Exiting context manager')
        self.close()
