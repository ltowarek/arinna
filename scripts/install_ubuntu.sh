#!/bin/sh
set -e

sudo apt-get update
sudo apt-get upgrade -y

sudo apt-get install -y mosquitto
sudo systemctl disable mosquitto

sudo apt-get install -y python3 python3-pip python3-virtualenv
python3 -m virtualenv -p python3 venv

. ../venv/bin/activate
pip install -r requirements.txt
deactivate

sudo apt-get install -y wget
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.6.0_amd64.deb
sudo dpkg -i influxdb_1.6.0_amd64.deb
rm influxdb_1.6.0_amd64.deb
sudo systemctl disable influxdb

sudo apt-get install -y wget
wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_5.2.1_amd64.deb
sudo dpkg -i grafana_5.2.1_amd64.deb
rm grafana_5.2.1_amd64.deb
sudo systemctl disable grafana-server

mkdir -p logs
