#!/bin/bash
mode=default
[ $# -ge 1 ] && mode=PowerOn
if [ "$mode" == "PowerOn" ];then
    ifconfig eth0 down
    ifconfig eth0 hw ether 02:0a:35:00:01:10
    ifconfig eth0 up
    ifconfig eth0 192.168.99.10
    ifconfig eth0 netmask 255.255.255.0
    route add default gw 192.168.99.1
elif [ "$mode" == "user" ];then
    ifconfig eth0 down
    ifconfig eth0 hw ether 
    ifconfig eth0 up
    ifconfig eth0 
    ifconfig eth0 netmask 
    route add default gw
elif [ "$mode" == "default" ];then
    ifconfig eth0 down
    ifconfig eth0 hw ether 02:0a:35:00:01:11
    ifconfig eth0 up
    ifconfig eth0 192.168.99.11
    ifconfig eth0 netmask 255.255.255.0
    route add default gw 
fi
