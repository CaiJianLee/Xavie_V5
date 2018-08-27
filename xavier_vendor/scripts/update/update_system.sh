#########################################################################
# File Name: update_system.sh
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
UP_DATA_FOLDER=$1

if [ $# -lt 1 ]; then
	echo "input param less then 1"
	echo "USAGE: $0 [updata folder]"
	echo "	EXAMPLE: $0 /opt/seeing/tftpboot"
	exit 1
fi

function check_file_exist(){
	if [ ! -f $1 ];then
		echo "  update_system $1 not exist"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]$1 not exist"
		return 0
	else
		echo "  update_system $1 exist"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]$1 exist"
		PACK_FILE+=" $1"
		return 1
	fi
}

cd $UP_DATA_FOLDER

check_file_exist uImage
check_file_exist fpga.bit
check_file_exist devicetree.dtb

check_file_exist zImage
check_file_exist am335x-boneblack.dtb
check_file_exist uEnv.txt
check_file_exist ML0

if [  -n "$PACK_FILE" ];then
	echo "  update_system $PACK_FILE update start ..."
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system $PACK_FILE update start ..."
	mount /dev/mmcblk0p1 /mnt
	if [ $? -ne 0 ];then
		echo "  update_system mount /dev/mmcblk0p1 failed"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system mount /dev/mmcblk0p1 failed"
		exit 1
	fi
	cd $UP_DATA_FOLDER
	mkdir back_up
	cp /mnt/* ./back_up
	
	if [ -f ./back_up/bootmd5.txt ];then
		cp ./back_up/bootmd5.txt /mnt
	fi
	
	cp $PACK_FILE /mnt
	if [ $? -ne 0 ];then
		cp ./back_up/* /mnt
		echo "  update_system failed, back to the previous version"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system failed, back to the previous version."
		exit 1
	fi

	rm back_up -rf
	cd /mnt
	cd -
	sync
	umount /mnt
	echo "  update_system $PACK_FILE update success"
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system $PACK_FILE update success"
	
else
	echo "  update_system not have \"uImage fpga.bit devicetree.dtb\" file"
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system not have \"uImage fpga.bit devicetree.dtb\" file"
fi

if [ -f $UP_DATA_FOLDER/modules_*.tar.gz ];then
	cd $UP_DATA_FOLDER
	MODULES=`ls modules_*.tar.gz`
	echo "  update_system $MODULES exist ..."
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system $MODULES exist ..."
	echo "  update_system backup /lib/modules/ folder "
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system backup /lib/modules/ folder "
	mkdir backup_modules
	[ -d /lib/modules/ ] && cp -ardf /lib/modules/ ./backup_modules/
	rm -rf /lib/modules/
	echo "  update_system start update /lib/modules/ folder "
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system start update /lib/modules/ folder "
	tar mzxf $MODULES -C /lib/
	if [ $? -ne 0 ];then
		rm -rf /lib/modules
		cp -ardf ./backup_modules/modules /lib/
		echo "  update_system update $MODULES failed, back to the previous version"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_system]update_system update $MODULES failed, back to the previous version."
	fi
fi

[ $UP_DATA_FOLDER/../app/scripts/env.sh ] && cp -rf $UP_DATA_FOLDER/../app/scripts/env.sh /etc/profile.d/
[ -f $UP_DATA_FOLDER/80-seeing.rules ] && cp -rf $UP_DATA_FOLDER/80-seeing.rules /etc/udev/rules.d/
exit 0
