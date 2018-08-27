#########################################################################
# File Name: restart.sh
# Author: zhen
# mail: qingzhen.zhu@gzseeing.com 
# Created Time: 2016年11月04日 星期五 13时15分43秒
#########################################################################
#!/bin/bash

if [ "$1" == "" ];then
    killall -9 monitor ee cmd daq fwdl1 fwdl2 fwdl3 fwdl4
    [ -d "/sys/class/gpio/gpio913" ] && echo 913 > /sys/class/gpio/unexport
    /bin/bash /opt/seeing/app/scripts/start.sh "network_no_reset"
    exit 0
elif [ "$1" == "ee" ];then
    [ -d "/sys/class/gpio/gpio913" ] && echo 913 > /sys/class/gpio/unexport
fi

killall -9 $1 >/dev/null
/bin/bash /opt/seeing/app/scripts/start.sh "network_no_reset" $1
