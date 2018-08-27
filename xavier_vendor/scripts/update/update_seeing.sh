#########################################################################
# File Name: update_seeing.sh
# Author: zhen
# mail: qingzhen.zhu@126.com
# Created Time: 2016年09月18日 星期日 15时28分09秒
# modify Author:weizhenhua
# mail: zhenhua.wei@gzseeing.com
# modify time: 2017年8月31日 星期四 14时07分3秒
#########################################################################
#!/bin/bash

# 获取当前文件的目录
LOCAL_FILE=$(cd "$(dirname "$0")";pwd)
SEEING_TAR_FILE=seeing.tar.gz
APP_TAR_FILE=app.tar.gz
UP_DATA_FOLDER=$1
APP_FOLDER=/opt/seeing/app

[ -f /opt/seeing/tftpboot/$SEEING_TAR_FILE ] && PACK_FILE=$SEEING_TAR_FILE
[ -f /opt/seeing/tftpboot/$APP_TAR_FILE ] && PACK_FILE=$APP_TAR_FILE

if [ $# -lt 1 ]; then
	echo "input param less then 1"
	echo "USAGE: $0 [updata folder]"
	echo "	EXAMPLE: $0 /opt/seeing/tftpboot"
	exit 1
fi

cd $UP_DATA_FOLDER
if [ ! -f $PACK_FILE ];then
	echo "  update_seeing $PACK_FILE not exist"
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_seeing]$PACK_FILE not exist"
	exit 0
fi

echo "  update_seeing $PACK_FILE update start ..."
/bin/bash $LOCAL_FILE/../update_log.sh "[update_seeing]$PACK_FILE update start ..."
# cd $LOCAL_FILE/../../
cd $APP_FOLDER

mkdir $UP_DATA_FOLDER/seeing_backups 
cp * $UP_DATA_FOLDER/seeing_backups  -rf
rm -rf *
cp $UP_DATA_FOLDER/$PACK_FILE ./


echo "  update_seeing update files exist"
tar -mzxf $PACK_FILE
if [ $? -ne 0 ];then
	rm -rf *
	cp $UP_DATA_FOLDER/seeing_backups/* . -rf
	echo "  update_seeing failed, back to the previous version"
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_seeing]update_seeing failed, back to the previous version."
	exit 1
fi

rm -rf $PACK_FILE

sync
[ ! -d $UP_DATA_FOLDER/../config ] && mkdir $UP_DATA_FOLDER/../config
[ ! -f $UP_DATA_FOLDER/../config/network.sh ] && cp -rf $UP_DATA_FOLDER/../app/scripts/network.sh $UP_DATA_FOLDER/../config/
echo "  update_seeing success"
/bin/bash $LOCAL_FILE/../update_log.sh "[update_seeing]update_seeing success."
exit 0
