#!/usr/bin/env python3

import arinna.inverter_provider as inverter_provider
import logging
import arinna.log as log
import sys
import arinna.database_provider as database_provider

logger = logging.getLogger(__name__)


def main():
    log.setup_logging()

    with database_provider.MQTTClient() as mqtt_client:
        publisher = inverter_provider.InverterMQTTPublisher(mqtt_client)
        publisher.publish_request('QPIGS')

    return 0


if __name__ == '__main__':
    sys.exit(main())
