###########################################################
# File Name: test_amp.sh
# Author: Lihong
# mail: lihong@gzseeing.com 
# Modify Time: 2018-04-08
###########################################################
#!/bin/bash
#
# test openamp remoteproc, rpmsg, and uart0
#
PWD=$(cd "$(dirname "$0")";pwd)
FW=app1.elf
FW_LINUX=app0.elf


function usage() {
    echo "**************************************"
    echo ""
    echo "Usage: sh $0 <test_cnt>"
    echo ""
    echo "**************************************"
}

if [ ! $# == 1 ]; then
    usage
    exit 0
fi


[ ! -d /lib/firmware ] && mkdir -p /lib/firmware
cp -f ${PWD}/${FW} /lib/firmware
sync
sleep 1


modprobe -r rpmsg_user_dev_driver
modprobe -r zynq_remoteproc
sleep 0.5
modprobe zynq_remoteproc
sleep 0.2
modprobe rpmsg_core
sleep 0.2
insmod ${PWD}/rpmsg_user_dev_driver_for_test.ko
sleep 0.2


echo ""
echo "OpenAMP test start..."


if [ -d /sys/class/remoteproc/remoteproc0 ]
then
    echo ${FW} > /sys/class/remoteproc/remoteproc0/firmware
    echo "FW: $(cat /sys/class/remoteproc/remoteproc0/firmware)"
    sleep 0.2
else 
    echo "Error:OpenAMP firmwork could be wrong, please check it!"
    exit 1
fi


echo "test start time :" > ${PWD}/result.txt
date "+%Y-%m-%d %H:%M:%S %Z" >> ${PWD}/result.txt
time1=$(date "+%Y-%m-%d %H:%M:%S")


chmod +x ${PWD}/${FW_LINUX}
for i in $(seq 1 $1)
do
    echo "[test cnt -- $i]"
    echo start > /sys/class/remoteproc/remoteproc0/state
    sleep 0.3
    ${PWD}/${FW_LINUX}
    echo stop > /sys/class/remoteproc/remoteproc0/state
    sleep 0.3
done


echo "test end time :" >> ${PWD}/result.txt
date "+%Y-%m-%d %H:%M:%S %Z" >> ${PWD}/result.txt
time2=$(date "+%Y-%m-%d %H:%M:%S")

# echo $time2
# echo $time1
# echo $(date -d "$time2" +%s)
# echo $(date -d "$time1" +%s)

time_test=$(($(date -d "$time2" +%s) - $(date -d "$time1" +%s)))
echo "test count: $1" >> ${PWD}/result.txt
echo "test spend time: $time_test seconds" >> ${PWD}/result.txt
echo "test over!">> ${PWD}/result.txt
echo "test spend time: $time_test seconds"
echo "test over!"
echo ""


rm -rf /lib/firmware/${FW}
rmmod rpmsg_user_dev_driver_for_test
chmod -x ${PWD}/${FW_LINUX}
sleep 0.2

