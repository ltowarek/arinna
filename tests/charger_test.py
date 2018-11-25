from datetime import time
from arinna.charger import ChargingManager


def test_charging_manager_is_in_cheap_day_rate():
    assert False is ChargingManager.is_in_cheap_day_rate(time(12, 59))
    assert True is ChargingManager.is_in_cheap_day_rate(time(13, 0))
    assert True is ChargingManager.is_in_cheap_day_rate(time(14, 0))
    assert True is ChargingManager.is_in_cheap_day_rate(time(14, 59))
    assert False is ChargingManager.is_in_cheap_day_rate(time(15, 0))


def test_charging_manager_is_in_cheap_night_rate():
    assert False is ChargingManager.is_in_cheap_night_rate(time(21, 59))
    assert True is ChargingManager.is_in_cheap_night_rate(time(22, 0))
    assert True is ChargingManager.is_in_cheap_night_rate(time(23, 0))
    assert True is ChargingManager.is_in_cheap_night_rate(time(0, 0))
    assert True is ChargingManager.is_in_cheap_night_rate(time(1, 0))
    assert True is ChargingManager.is_in_cheap_night_rate(time(2, 0))
    assert True is ChargingManager.is_in_cheap_night_rate(time(3, 0))
    assert True is ChargingManager.is_in_cheap_night_rate(time(4, 0))
    assert True is ChargingManager.is_in_cheap_night_rate(time(5, 0))
    assert True is ChargingManager.is_in_cheap_night_rate(time(5, 59))
    assert False is ChargingManager.is_in_cheap_night_rate(time(6, 0))
