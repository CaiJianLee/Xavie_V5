#!/bin/bash

function reset_eth0_phy(){
    if [ -d /sys/class/gpio/gpio919 ]; then
        echo 919 > /sys/class/gpio/unexport
    fi
    echo 919 > /sys/class/gpio/export
    echo out > /sys/class/gpio/gpio919/direction
    echo 0 > /sys/class/gpio/gpio919/value
    sleep 0.05
    echo 1 > /sys/class/gpio/gpio919/value
}

reset_eth0_phy

