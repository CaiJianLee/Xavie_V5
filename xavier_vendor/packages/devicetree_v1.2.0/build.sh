###########################################
# File Name: build.sh
# Author: Lihong
# mail: lihong@gzseeing.com
# Modified Time: 2018-03-26
###########################################
#!/bin/bash

function usage()
{
    echo "###################################"
    echo ""
    echo "Usage: sh build.sh [amp | clean]"
    echo ""
    echo "###################################"
}

PWD=$(cd "$(dirname "$0")";pwd)


if [ $# -gt 1 ]
then
    usage
    exit 0
fi

if [ $# == 1 ]
then
    if [ "$1" != "amp" -a "$1" != "clean" ]
    then
        usage
        exit 0
    fi
fi

if [ $# == 1 ]
then
    args=$1
else
    args="null"
fi


if [ -f ${PWD}/pl_*.dtsi ]
then
    cp -f ${PWD}/pl_*.dtsi ${PWD}/pl.dtsi
fi



if [ $args == "clean" ]
then
    rm -rf ${PWD}/devicetree.dtb
    if [ -f ${PWD}/pl_*.dtsi ]
    then
        rm -rf ${PWD}/pl.dtsi
    fi
else
    if [ $args == "amp" ]
    then
        dtc -O dtb -I dts -o ${PWD}/devicetree.dtb ${PWD}/system_amp.dts
        echo ""
        echo "build xavier devicetree.dtb [with amp]"
        echo ""
    else
        dtc -O dtb -I dts -o ${PWD}/devicetree.dtb ${PWD}/system.dts
        echo ""
        echo "build xavier devicetree.dtb [without amp]"
        echo ""
    fi
fi

