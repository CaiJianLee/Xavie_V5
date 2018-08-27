#!/bin/sh
 
dfulib_path=/opt/seeing/app/lib:/opt/seeing/app/packages/dfulib
dfuserver_elf=/opt/seeing/app/packages/dfuserver/dfu_rpc_server

# cd /opt/seeing/app/fwdl_config/

for file in /opt/seeing/app/packages/dfulib/*
do  
    echo $file
   if [ -e $file ];then
       echo $dfulib_path
        /opt/seeing/app/fwdl_config/patchelf --set-rpath $dfulib_path $file
    else
        echo $file is not exist
    fi
done

echo $dfuserveer_elf
if [ -e $dfuserver_elf ];then
    /opt/seeing/app/fwdl_config/patchelf --set-rpath $dfulib_path $dfuserver_elf
else
    echo $dfuserver_elf is not exist
fi
#

