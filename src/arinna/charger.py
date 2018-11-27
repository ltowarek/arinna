#!/usr/bin/env python3

from datetime import datetime, time
import logging
import arinna.log as log
import sys
from arinna.database_client import DatabaseClient

logger = logging.getLogger(__name__)


class ChargingManager:
    def __init__(self, database, charger):
        self.database = database
        self.charger = charger

    def process(self, now):
        if self.is_in_cheap_day_rate(now):
            is_ac_charging_on = self.database.moving_average(
                'is_ac_charging_on', '5m')
            battery_voltage = self.database.moving_max('battery_voltage', '5m')
            is_charging_to_floating_enabled = \
                self.database.moving_true_percentage(
                    'is_charging_to_floating_enabled', '5m')

            if is_ac_charging_on == 0:
                self.charger.disable()
            elif (
                    is_charging_to_floating_enabled == 1.0
                    and battery_voltage < 56.4
            ) or (
                    is_charging_to_floating_enabled == 0.0
                    and battery_voltage < 54.0
            ):
                self.charger.enable()
            else:
                logger.info('Leaving charger as is')
        elif self.is_in_cheap_night_rate(now):
            battery_voltage = self.database.moving_min('battery_voltage', '5m')
            is_charging_to_floating_enabled = \
                self.database.moving_true_percentage(
                    'is_charging_to_floating_enabled', '3h')

            if is_charging_to_floating_enabled == 1.0:
                self.charger.disable()
            elif battery_voltage < 48.0:
                self.charger.enable()
            else:
                logger.info('Leaving charger as is')
        else:
            self.charger.disable()

    @staticmethod
    def is_in_cheap_day_rate(now):
        return time_in_range(time(13), time(15), now)

    @staticmethod
    def is_in_cheap_night_rate(now):
        return time_in_range(time(22), time(6), now)


def time_in_range(start, end, x):
    if start <= end:
        return start <= x < end
    else:
        return start <= x or x < end


class Charger:
    def __init__(self, database):
        self.database = database

    def enable(self):
        logger.info('Enabling charger')
        self.set_state(True)
        logger.info('Charger enabled')

    def disable(self):
        logger.info('Disabling charger')
        self.set_state(False)
        logger.info('Charger disabled')

    def set_state(self, is_enabled):
        logger.info('Setting charger state')
        self.database.save('is_enabled', is_enabled)
        logger.info('Charger state set')


def main():
    log.setup_logging()

    try:
        with DatabaseClient(db_name='charger') as charger_database, \
                DatabaseClient() as inverter_database:
            charger = Charger(charger_database)
            charging_manager = ChargingManager(inverter_database, charger)
            now = datetime.now().time()
            charging_manager.process(now)
    except Exception:
        logger.exception('Unknown exception occurred')

    return 0


if __name__ == '__main__':
    sys.exit(main())
