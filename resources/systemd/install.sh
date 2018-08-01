#!/bin/sh

sudo cp \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-scheduler.service \
    arinna.target \
    /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-scheduler.service \

# Uncomment to enable boot loading
#sudo systemctl enable arinna.target
