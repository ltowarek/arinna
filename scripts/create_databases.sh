#!/bin/sh
set -e

curl -POST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE inverter"
curl -POST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE load"
curl -POST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE charger"

curl -POST http://localhost:8086/query --data-urlencode "q=CREATE RETENTION POLICY "one_year" ON "inverter" DURATION 52w REPLICATION 1"
curl -POST http://localhost:8086/query --data-urlencode "q=CREATE RETENTION POLICY "one_year" ON "load" DURATION 52w REPLICATION 1"
curl -POST http://localhost:8086/query --data-urlencode "q=CREATE RETENTION POLICY "one_year" ON "charger" DURATION 52w REPLICATION 1"
