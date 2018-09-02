#!/usr/bin/env python3

import arinna.load_balancer as lb


def test_can_add_load_returns_false_without_readings():
    assert False is lb.can_add_load(None, None)
    assert False is lb.can_add_load(1, None)
    assert False is lb.can_add_load(None, 1)


def test_can_add_load_returns_false_without_fully_charged_battery():
    assert False is lb.can_add_load(55.0, 0.5)


def test_can_add_load_returns_false_without_maximum_power_point_reached():
    assert False is lb.can_add_load(56.0, 1.0)


def test_can_add_load_returns_true_with_fully_charged_battery():
    assert True is lb.can_add_load(56.0, 0.5)
    assert True is lb.can_add_load(57.0, 0.5)
    assert True is lb.can_add_load(58.0, 0.5)


def test_can_add_load_returns_true_with_maximum_power_point_reached():
    assert True is lb.can_add_load(56.0, 0.5)
    assert True is lb.can_add_load(56.0, 0.1)
    assert True is lb.can_add_load(56.0, 0.9)
