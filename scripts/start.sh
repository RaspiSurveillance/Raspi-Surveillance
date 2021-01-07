#!/bin/bash

cd src
if [[ ! -e /tmp/raspi-surveillance.py.pid ]]; then
    echo "Starting Raspi-Surveillance..."
    python3 raspi-surveillance.py &
    echo $! > /tmp/raspi-surveillance.py.pid
    echo "Raspi-Surveillance has been started with pid "
    cat /tmp/raspi-surveillance.py.pid
else
    echo -n "ERROR: Raspi-Surveillance seems to be running with pid "
    cat /tmp/raspi-surveillance.py.pid
    echo
fi
