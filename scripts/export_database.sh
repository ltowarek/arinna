#!/bin/sh
set -e

curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"ac_output_active_power\"" > ac_output_active_power.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"ac_output_apparent_power\"" > ac_output_apparent_power.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"ac_output_frequency\"" > ac_output_frequency.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"ac_output_voltage\"" > ac_output_voltage.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"battery_capacity\"" > battery_capacity.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"battery_charging_current\"" > battery_charging_current.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"battery_discharge_current\"" > battery_discharge_current.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"battery_voltage\"" > battery_voltage.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"battery_voltage_from_scc\"" > battery_voltage_from_scc.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"battery_voltage_offset_for_fans_on\"" > battery_voltage_offset_for_fans_on.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"bus_voltage\"" > bus_voltage.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"eeprom_version\"" > eeprom_version.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"grid_frequency\"" > grid_frequency.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"grid_voltage\"" > grid_voltage.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"inverter_heat_sink_temperature\"" > inverter_heat_sink_temperature.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_ac_charging_on\"" > is_ac_charging_on.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_battery_voltage_to_steady_while_charging\"" > is_battery_voltage_to_steady_while_charging.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_charging_on\"" > is_charging_on.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_charging_to_floating_enabled\"" > is_charging_to_floating_enabled.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_configuration_changed\"" > is_configuration_changed.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_dustproof_installed\"" > is_dustproof_installed.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_load_on\"" > is_load_on.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_sbu_priority_version_added\"" > is_sbu_priority_version_added.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_scc_charging_on\"" > is_scc_charging_on.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_scc_firmware_updated\"" > is_scc_firmware_updated.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"is_switch_on\"" > is_switch_on.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"output_load_percent\"" > output_load_percent.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"pv_charging_power\"" > pv_charging_power.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"pv_input_current_for_battery\"" > pv_input_current_for_battery.csv
curl -H "Accept: application/csv" -G "http://localhost:8086/query?db=inverter" --data-urlencode "q=SELECT * FROM \"pv_input_voltage\"" > pv_input_voltage.csv
