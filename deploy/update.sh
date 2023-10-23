#! /bin/bash

if [ $# -eq 0 ]; then
    echo "Please enter target IP address"
    exit 1
fi

IP=$1
TARGET=/home/pi/heater_cycle_test

echo "removing old pip installation of lib"
ssh pi@$IP "pip3 uninstall heater-cycler"

scp -r lib/ pi@$IP:$TARGET
scp -r requirements.txt pi@$IP:$TARGET
scp -r main.py pi@$IP:$TARGET

echo "installing library via pip"
ssh pi@$IP "cd $TARGET/lib && pip3 install ."

