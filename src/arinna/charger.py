#!/usr/bin/env python3

from datetime import datetime, time
import logging
import arinna.log as log
import arinna.mqtt_client
import arinna.inverter_provider as inverter_provider
import sys
from arinna.database_client import DatabaseClient

logger = logging.getLogger(__name__)


class ChargingManager:
    def __init__(self, database, charger):
        self.database = database
        self.charger = charger

    def process(self, now):
        if self.is_in_cheap_day_rate(now):
            logger.info('In cheap day rate')
            battery_voltage = self.database.moving_max('battery_voltage', '5m')
            is_charging_to_floating_enabled = \
                self.database.moving_true_percentage(
                    'is_charging_to_floating_enabled', '5m')

            if (
                    is_charging_to_floating_enabled == 1.0
                    and battery_voltage < 52.0
            ) or (
                    is_charging_to_floating_enabled == 0.0
                    and battery_voltage < 55.0
            ):
                self.charger.enable()
            else:
                logger.info('Leaving charger as is')
        elif self.is_in_cheap_night_rate(now):
            logger.info('In cheap night rate')
            battery_voltage = self.database.moving_average('battery_voltage',
                                                           '5m')
            is_charging_to_floating_enabled = \
                self.database.moving_true_percentage(
                    'is_charging_to_floating_enabled', '3h')

            if is_charging_to_floating_enabled == 1.0:
                self.charger.disable()
            elif battery_voltage < 47.2:
                self.charger.enable()
            else:
                logger.info('Leaving charger as is')
        else:
            logger.info('Not in cheap rate')
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
    def __init__(self, inverter):
        self.inverter = inverter

    def enable(self):
        logger.info('Enabling charger')
        self.inverter.publish_request('POP00')
        self.inverter.publish_request('PCP02')
        self.inverter.publish_request('MUCHGC030')
        logger.info('Charger enabled')

    def disable(self):
        logger.info('Disabling charger')
        self.inverter.publish_request('POP02')
        self.inverter.publish_request('PCP01')
        self.inverter.publish_request('MUCHGC010')
        logger.info('Charger disabled')


def main():
    log.setup_logging()

    try:
        with arinna.mqtt_client.MQTTClient() as mqtt_client, \
                DatabaseClient() as inverter_database:
            mqtt_client.loop_start()
            publisher = inverter_provider.InverterMQTTPublisher(mqtt_client)
            charger = Charger(publisher)
            charging_manager = ChargingManager(inverter_database, charger)
            now = datetime.now().time()
            charging_manager.process(now)
            mqtt_client.loop_stop()
    except Exception:
        logger.exception('Unknown exception occurred')

    return 0


if __name__ == '__main__':
    sys.exit(main())
