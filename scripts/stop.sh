#!/bin/bash

if [[ -e /tmp/raspi-surveillance.py.pid ]]; then
    echo "Raspi-Surveillance is running, stopping..."
    kill `cat /tmp/raspi-surveillance.py.pid`
    rm /tmp/raspi-surveillance.py.pid
    echo "Raspi-Surveillance has been stopped"
else
    echo "Raspi-Surveillance is not running"
fi
