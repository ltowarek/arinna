#!/usr/bin/env python3

import logging
import logging.handlers
import os
import sys
import arinna.config as config
import arinna.database_provider as db

logger = logging.getLogger(__name__)


def can_add_load(battery_voltage, pv_voltage_stddev):
    if not battery_voltage or not pv_voltage_stddev:
        return False
    if is_battery_fully_charged(battery_voltage) and \
            is_maximum_power_point_reached(pv_voltage_stddev):
        return True
    return False


def is_battery_fully_charged(voltage):
    return voltage >= 56.0


def is_maximum_power_point_reached(voltage_stddev):
    return voltage_stddev < 1.0


def set_additional_load_state(is_enabled):
    logger.info('Setting additional load state')
    with db.DatabaseClient('load') as client:
        client.save('is_enabled', is_enabled)
    logger.info('Additional load state set')


def enable_additional_load():
    logger.info('Enabling additional load')
    set_additional_load_state(True)
    logger.info('Additional load enabled')


def disable_additional_load():
    logger.info('Disabling additional load')
    set_additional_load_state(False)
    logger.info('Additional load disabled')


def setup_logging(logs_directory):
    logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(logs_directory, 'load_balancer.log'),
        interval=5, when='m', backupCount=1)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def main():
    settings = config.load()
    setup_logging(settings.logs_directory)

    try:
        with db.DatabaseClient() as client:
            battery_voltage = client.moving_average('battery_voltage', '1m')
            pv_input_voltage_stddev = client.moving_stddev('pv_input_voltage',
                                                           '1m')
        if can_add_load(battery_voltage, pv_input_voltage_stddev):
            enable_additional_load()
        else:
            disable_additional_load()
    except Exception:
        logger.exception('Unknown exception occurred')

    return 0


if __name__ == '__main__':
    sys.exit(main())
