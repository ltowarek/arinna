#!/usr/bin/env python3

import arinna.inverter_provider as inverter_provider
import logging
import arinna.log as log
import sys
import arinna.mqtt_client

logger = logging.getLogger(__name__)


def main():
    log.setup_logging()

    with arinna.mqtt_client.MQTTClient() as mqtt_client:
        publisher = inverter_provider.InverterMQTTPublisher(mqtt_client)
        publisher.publish_request('QPIGS')

    return 0


if __name__ == '__main__':
    sys.exit(main())
