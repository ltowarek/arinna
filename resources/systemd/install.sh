#!/bin/sh

cp \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-publisher.timer \
    arinna-load-balancer.service \
    arinna-load-balancer.timer \
    arinna-charger.service \
    arinna-charger.timer \
    arinna.target \
    /etc/systemd/system/
systemctl daemon-reload

systemctl enable \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-publisher.timer \
    arinna-load-balancer.service \
    arinna-load-balancer.timer \
    arinna-charger.service \
    arinna-charger.timer

systemctl start \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-publisher.timer \
    arinna-load-balancer.service \
    arinna-load-balancer.timer \
    arinna-charger.service \
    arinna-charger.timer
