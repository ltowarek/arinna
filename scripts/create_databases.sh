#!/bin/sh
set -e

curl -POST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE inverter"
curl -POST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE load"
curl -POST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE charger"
