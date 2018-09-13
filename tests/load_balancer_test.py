#!/usr/bin/env python3

from arinna.load_balancer import LoadBalancer


class FakeDatabase:
    moving_average_value = 56.0
    moving_stddev_value = 0.5

    def moving_average(self, measurement, _):
        if measurement == 'battery_voltage':
            return self.moving_average_value

    def moving_stddev(self, measurement, _):
        if measurement == 'pv_input_voltage':
            return self.moving_stddev_value


class FakeLoad:
    is_enabled = False

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False


def test_balance_enables_load_given_proper_values():
    fake_database = FakeDatabase()
    fake_load = FakeLoad()

    load_balancer = LoadBalancer(fake_database, fake_load)
    load_balancer.balance()

    assert True is fake_load.is_enabled


def test_balance_disables_load_given_battery_is_not_fully_charged():
    fake_database = FakeDatabase()
    fake_database.moving_average_value = 55.0

    fake_load = FakeLoad()
    fake_load.is_enabled = True

    load_balancer = LoadBalancer(fake_database, fake_load)
    load_balancer.balance()

    assert False is fake_load.is_enabled


def test_balance_disables_load_given_maximum_power_point_is_not_reached():
    fake_database = FakeDatabase()
    fake_database.moving_stddev_value = 1.0

    fake_load = FakeLoad()
    fake_load.is_enabled = True

    load_balancer = LoadBalancer(fake_database, fake_load)
    load_balancer.balance()

    assert False is fake_load.is_enabled
