#!/usr/bin/env python3

import logging
import arinna.log as log
import sys
from arinna.database_client import DatabaseClient

logger = logging.getLogger(__name__)


class LoadBalancer:
    def __init__(self, database, load):
        self.database = database
        self.load = load

    def balance(self):
        battery_voltage = self.database.moving_average('battery_voltage', '1m')
        pv_input_voltage_stddev = self.database.moving_stddev(
            'pv_input_voltage',
            '1m')
        if self.can_add_load(battery_voltage, pv_input_voltage_stddev):
            self.load.enable()
        else:
            self.load.disable()

    @classmethod
    def can_add_load(cls, battery_voltage, pv_voltage_stddev):
        if cls.is_battery_fully_charged(battery_voltage) and \
                cls.is_maximum_power_point_reached(pv_voltage_stddev):
            return True
        return False

    @staticmethod
    def is_battery_fully_charged(voltage):
        return voltage >= 56.0

    @staticmethod
    def is_maximum_power_point_reached(voltage_stddev):
        return voltage_stddev < 1.0


class Load:
    def __init__(self, database):
        self.database = database

    def enable(self):
        logger.info('Enabling load')
        self.set_state(True)
        logger.info('Load enabled')

    def disable(self):
        logger.info('Disabling load')
        self.set_state(False)
        logger.info('Load disabled')

    def set_state(self, is_enabled):
        logger.info('Setting  load state')
        self.database.save('is_enabled', is_enabled)
        logger.info('Load state set')


def main():
    log.setup_logging()

    try:
        with DatabaseClient(db_name='load') as load_database, \
                DatabaseClient() as inverter_database:
            load = Load(load_database)
            load_balancer = LoadBalancer(inverter_database, load)
            load_balancer.balance()
    except Exception:
        logger.exception('Unknown exception occurred')

    return 0


if __name__ == '__main__':
    sys.exit(main())
