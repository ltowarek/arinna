#!/usr/bin/env python3

import arinna.database_provider as db


def test_bool_from_string_true():
    assert True is db.bool_from_string('1')


def test_bool_from_string_false():
    assert False is db.bool_from_string('0')


def test_percent():
    assert 0.00 == db.percent(0)
    assert 0.01 == db.percent(1)
    assert 0.02 == db.percent(2)
    assert 0.10 == db.percent(10)
    assert 0.20 == db.percent(20)
    assert 1.00 == db.percent(100)


def test_int_from_device_mode():
    assert 0 == db.int_from_device_mode('Power On')
    assert 1 == db.int_from_device_mode('Standby')
    assert 2 == db.int_from_device_mode('Line')
    assert 3 == db.int_from_device_mode('Battery')
    assert 4 == db.int_from_device_mode('Fault')
    assert 5 == db.int_from_device_mode('Power Saving')
