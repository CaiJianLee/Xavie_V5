#########################################################################
# File Name: update_u-boot.sh
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
	exit 0
fi

function check_file_exist_xavier(){
	if [ ! -f $1 ];then
		echo "  update_u-boot $1 not exist"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]$1 not exist"
		return 0
	else
		echo "  update_u-boot $1 exist"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]$1 exist"
		mount /dev/mmcblk0p1 /mnt
		if [ $? -ne 0 ];then
			echo "  update_u-boot mount /dev/mmcblk0p1 failed"
			/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot mount /dev/mmcblk0p1 failed"
			exit 1
		fi
		if [ -f /mnt/bootmd5.txt ];then
			cp /mnt/bootmd5.txt $UP_DATA_FOLDER/
			ERROR_MESSAGE=`md5sum -c bootmd5.txt | grep -w 'FAILED'`
			if [ -n "$ERROR_MESSAGE" ];then
				PACK_FILE_XAVIER+=" $UP_DATA_FOLDER/$1"
				return 1
			fi
			echo "  update_u-boot BOOT.bin is the same, not to update BOOT.bin"
			/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot BOOT.bin is the same, not to update BOOT.bin"
			umount /mnt
			return 0
		else
			PACK_FILE_XAVIER+=" $UP_DATA_FOLDER/$1"
			return 1
		fi
	fi
}

function check_file_exist_335x(){
	if [ ! -f $1 ];then
		echo "  update_u-boot $1 not exist"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]$1 not exist"
		return 0
	else
		echo "  update_u-boot $1 exist"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]$1 exist"

		PACK_FILE_335X+=" $UP_DATA_FOLDER/$1"
		return 1
	fi
}

cd $UP_DATA_FOLDER

check_file_exist_xavier BOOT.bin
check_file_exist_335x   u-boot.img


if [  -n "$PACK_FILE_XAVIER" ];then
	echo "  update_u-boot $PACK_FILE_XAVIER update start ..."
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot $PACK_FILE_XAVIER update start ..."
	cp /dev/mtd0 ./back_0.bin
	cp /dev/mtd1 ./back_1.bin

	flashcp -v $PACK_FILE_XAVIER /dev/mtd0
	flashcp -v $PACK_FILE_XAVIER /dev/mtd1
	if [ $? -ne 0 ];then
		flashcp back_0.bin /dev/mtd0
		flashcp back_1.bin /dev/mtd1
		echo "  update_u-boot failed, back to the previous version"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot failed, back to the previous version."
		umount /mnt
		exit 1
	fi
	md5sum $PACK_FILE_XAVIER > $UP_DATA_FOLDER/bootmd5.txt
	cp $UP_DATA_FOLDER/bootmd5.txt  /mnt/
	umount /mnt
	echo "  update_u-boot $PACK_FILE_XAVIER update success"
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot $PACK_FILE_XAVIER update success"

	sync
	exit 0
elif [  -n "$PACK_FILE_335X" ];then
	echo "  update_u-boot.img$PACK_FILE_335X update start ..."
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot $PACK_FILE_335X update start ..."
	
	# cp /dev/mtd0 ./back.bin
	# flashcp -v $PACK_FILE_335X /dev/mtd0
	mount /dev/mmcblk0p1 /mnt
	if [ $? -ne 0 ];then
		echo "  update_u-boot mount /dev/mmcblk0p1 failed"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot mount /dev/mmcblk0p1 failed"
		exit 1
	fi
	cd $UP_DATA_FOLDER
	mkdir back_up
	cp /mnt/u-boot.img  back_up
	cp $PACK_FILE_335X  /mnt
	if [ $? -ne 0 ];then
		cp back_up/u-boot.img  /mnt/
		echo "  update_u-boot failed, back to the previous version"
		/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot failed, back to the previous version."
		umount /mnt
		exit 1
	fi

	umount /mnt
	echo "  update_u-boot $PACK_FILE_335X update success"
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]update_u-boot $PACK_FILE_335X update success"

	sync
	exit 0

else
	echo "  not to update u-boot, not have \"BOOT.bin\" file or \"BOOT.bin\" is the same."
	/bin/bash $LOCAL_FILE/../update_log.sh "[update_u-boot]not to update u-boot, not have \"BOOT.bin\" file or \"BOOT.bin\" is the same."
fi

exit 0
