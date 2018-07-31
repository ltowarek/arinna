#!/usr/bin/env python3

import os
import sys
import yaml


class Config:
    def __init__(self):
        self.settings = {
            'logs_directory': '',
            'serial_port': '',
        }

    def from_yaml(self, path):
        with open(path) as f:
            self.settings.update(yaml.safe_load(f))

    def __getattr__(self, name):
        return self.settings[name]

    def __str__(self):
        return str(self.settings)


def load():
    config = Config()
    path = config_path()
    if os.path.exists(path):
        config.from_yaml(config_path())
    return config


def config_path():
    return os.environ.get('ARINNA_CONFIG', '/etc/arinna/config.yaml')


def main():
    print('Config path: {}'.format(config_path()))
    print('Config:\n{}'.format(load()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
