#!/bin/sh

mkdir -p ~/.config/systemd/user/

cp \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-publisher.timer \
    arinna-load-balancer.service \
    arinna-load-balancer.timer \
    arinna.target \
    ~/.config/systemd/user/
systemctl --user daemon-reload

systemctl --user enable \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-publisher.timer \
    arinna-load-balancer.service \
    arinna-load-balancer.timer \

systemctl --user enable \
    arinna-database.service \
    arinna-inverter.service \
    arinna-publisher.service \
    arinna-publisher.timer \
    arinna-load-balancer.service \
    arinna-load-balancer.timer \

# Uncomment to enable boot loading
#systemctl --user enable arinna.target
