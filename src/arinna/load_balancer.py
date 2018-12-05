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
        device_mode = self.database.moving_average('device_mode', '5m')
        battery_voltage = self.database.moving_average('battery_voltage', '5m')
        pv_input_voltage = self.database.moving_average('pv_input_voltage',
                                                        '5m')
        is_charging_to_floating_enabled = \
            self.database.moving_true_percentage(
                'is_charging_to_floating_enabled', '5m')

        if device_mode == 3.0 and \
                pv_input_voltage > 95.0 and \
                (
                        (battery_voltage >= (56.4 - 0.4) and
                         is_charging_to_floating_enabled == 0.0)
                        or
                        (battery_voltage >= (54.0 - 0.4) and
                         is_charging_to_floating_enabled == 1.0)
                ):
            self.load.enable()
        else:
            self.load.disable()


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
