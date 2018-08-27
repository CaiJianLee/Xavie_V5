#########################################################################
# File Name: Armboard.sh
# Author: zhen
# mail: qingzhen.zhu@126.com
# Created Time: 2016年09月18日 星期日 15时28分09秒
#########################################################################
#!/bin/bash

# 获取当前文件的目录
LOCAL_FILE=$(cd "$(dirname "$0")";pwd)
#EXEC_FILE

PACK_FILE=seeing.tar.gz
echo "-------------------- $0 --------------------"

# 1 杀掉当前正在运行的程序
killall -9 monitor ee cmd daq

rmmod axi4lite
rmmod axi4stream

# 2 解压打包传上来的文件，到当前目录
cd $LOCAL_FILE
pwd
mv  $PACK_FILE ../
rm -rf *
#rm -rf bin drives_modules sepyd scripts config handles selib
#mkdir pack
#mv  arm_run.sh pack.tar pack/
#cd pack
pwd
mv ../$PACK_FILE ./
tar -mxvf $PACK_FILE 
#cp -rf bin drives_modules sepyd scripts config handles selib ../
#cp -rf *  ../
#cd ../
pwd
rm -rf $PACK_FILE 

# 3 启动上传的新程序  挂起执行 & 
#export PATH=$LOCAL_FILE/bin:$LOCAL_FILE/../python/bin:$PATH
#export LD_LIBRARY_PATH=$LOCAL_FILE/lib:$LOCAL_FILE/../lib:$LOCAL_FILE/../lib/arm-linux-gnueabihf:$LOCAL_FILE/../python/lib:$LD_LIBRARY_PATH
#export PYTHON_HOME=/opt/seeing/app
#export PYTHONPATH=$PYTHON_HOME/sepyd:$PYTHON_HOME/sepyd/common:$PYTHON_HOME/sepyd/devices:$PYTHONPATH

#cd $LOCAL_FILE/bin
#		dd if=/dev/zero of=/opt/seeing/app/config/testio bs=8 count=1000
pwd
#sehwad &
#secpd &
#echo "run the secpd"
#echo "run the sehwad"
/bin/bash /opt/seeing/app/scripts/start.sh
echo "-------------------- $0 end --------------------"
