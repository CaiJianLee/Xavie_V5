###########################################################
# File Name: amp.sh
# Author: Lihong
# mail: lihong@gzseeing.com 
# Modify Time: 2018-04-07
###########################################################
#!/bin/bash
#
# config and start amp firmware
#
PWD=$(cd "$(dirname "$0")";pwd)

# change it as your fw
FW=Demo.elf

echo "${PWD}/amp.sh start"

[ ! -d /lib/firmware ] && mkdir -p /lib/firmware
cp -f ${PWD}/${FW} /lib/firmware
sync
sleep 1

# exit 0

modprobe zynq_remoteproc

if [ -d /sys/class/remoteproc/remoteproc0 ]
then
    echo ${FW} > /sys/class/remoteproc/remoteproc0/firmware
    echo "FW: $(cat /sys/class/remoteproc/remoteproc0/firmware)"
    sleep 0.2
    echo start > /sys/class/remoteproc/remoteproc0/state
    sleep 0.5
    modprobe rpmsg_user_dev_driver
    sleep 0.2
    echo "OpenAMP is running"
else
    echo "Error:/sys/class/remoteproc/remoteproc0,no such file or directory!"
    exit 1
fi

