#!/usr/bin/env python3

import arinna.config as config
import logging.config
import yaml


def setup_logging():
    settings = config.load()
    with open(settings.logging_config) as f:
        c = yaml.safe_load(f)
    logging.config.dictConfig(c)
