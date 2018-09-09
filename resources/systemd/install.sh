#!/bin/sh

sudo cp \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-publisher.timer \
    arinna-load-balancer.service \
    arinna-load-balancer.timer \
    arinna.target \
    /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.timer \
    arinna-load-balancer.timer

# Uncomment to enable boot loading
#sudo systemctl enable arinna.target
