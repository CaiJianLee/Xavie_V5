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
    echo "Usage: sh build.sh [clean]"
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
    if [ "$1" != "clean" ]
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

if [ -f ${PWD}/FSBL_*.elf ]
then
    cp -f ${PWD}/FSBL_*.elf ${PWD}/FSBL.elf
fi

if [ -f ${PWD}/u-boot_*.elf ]
then
    cp -f ${PWD}/u-boot_*.elf ${PWD}/u-boot.elf
fi


if [ $args == "clean" ]
then
    rm -rf ${PWD}/BOOT.bin
    if [ -f ${PWD}/FSBL_*.elf ]
    then
        rm -rf ${PWD}/FSBL.elf
    fi
    if [ -f ${PWD}/u-boot_*.elf ]
    then
        rm -rf ${PWD}/u-boot.elf
    fi
else
    ${PWD}/bootgen -image boot.bif -o i BOOT.bin -w on
fi

