#! /bin/bash

if [ $# -eq 0 ]; then
    echo "Please enter target IP address"
    exit 1
fi

IP=$1
TARGET=/home/pi/heater_cycle_test

echo "removing existing target directory if present"
ssh pi@$IP "if [[ -d $TARGET ]]; then rm -rf $TARGET; fi"
echo "removing old pip installation of lib"
ssh pi@$IP "pip3 uninstall heater-cycler"

echo "copying source files to target destination"
ssh pi@$IP mkdir $TARGET
ssh pi@$IP mkdir $TARGET/log
ssh pi@$IP mkdir $TARGET/csv
ssh pi@$IP mkdir $TARGET/csv/channel_1/
ssh pi@$IP mkdir $TARGET/csv/channel_2/
ssh pi@$IP mkdir $TARGET/csv/channel_3/
ssh pi@$IP mkdir $TARGET/csv/channel_4/
ssh pi@$IP mkdir $TARGET/csv/channel_5/
ssh pi@$IP mkdir $TARGET/csv/channel_6/
ssh pi@$IP mkdir $TARGET/csv/channel_7/
ssh pi@$IP mkdir $TARGET/csv/channel_8/
ssh pi@$IP mkdir $TARGET/csv/channel_1/cycles/
ssh pi@$IP mkdir $TARGET/csv/channel_2/cycles/
ssh pi@$IP mkdir $TARGET/csv/channel_3/cycles/
ssh pi@$IP mkdir $TARGET/csv/channel_5/cycles/
ssh pi@$IP mkdir $TARGET/csv/channel_4/cycles/
ssh pi@$IP mkdir $TARGET/csv/channel_6/cycles/
ssh pi@$IP mkdir $TARGET/csv/channel_7/cycles/
ssh pi@$IP mkdir $TARGET/csv/channel_8/cycles/
scp -r config/ pi@$IP:$TARGET
scp -r lib/ pi@$IP:$TARGET
scp -r requirements.txt pi@$IP:$TARGET
scp -r main.py pi@$IP:$TARGET

echo "installing library via pip"
ssh pi@$IP "cd $TARGET/lib && pip3 install ."

