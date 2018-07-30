#!/bin/sh
set -e

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y wget
wget -O mosquitto-repo.gpg.key http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
sudo apt-key add mosquitto-repo.gpg.key
rm mosquitto-repo.gpg.key
sudo wget -O /etc/apt/sources.list.d/mosquitto-stretch.list http://repo.mosquitto.org/debian/mosquitto-stretch.list
sudo apt-get update
sudo apt-get install -y mosquitto
sudo systemctl disable mosquitto

sudo apt-get install -y python3 python3-pip python3-virtualenv
python3 -m virtualenv -p python3 venv

. ../venv/bin/activate
pip install -r requirements.txt
deactivate

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y apt-transport-https curl
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update
sudo apt-get install -y influxdb
sudo systemctl disable influxdb

sudo apt-get install -y apt-transport-https curl
curl https://bintray.com/user/downloadSubjectPublicKey?username=bintray | sudo apt-key add -
echo "deb https://dl.bintray.com/fg2it/deb stretch main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana
sudo systemctl disable grafana-server

mkdir -p logs
