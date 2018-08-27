#######################################################################
# File Name: update.sh
# Author: zhen
# mail: qingzhen.zhu@gzseeing.com 
# Created Time: 2016年12月13日 星期二 10时04分39秒
# modify Author:weizhenhua
# mail: zhenhua.wei@gzseeing.com 
# modify time: 2017年8月31日 星期四 14时07分3秒
#########################################################################
#!/bin/bash

LOCAL_FILE=/opt/seeing/app/scripts
UPDATE_FOLDER=/opt/seeing/tftpboot
UPDATE_FILE=ARM_Board_D3*.tar.gz
PACK_FILE=seeing.tar.gz
UPDATE_LOG_FILE=/opt/seeing/log/update.log

echo "Xavier update start..."

if [ -f $UPDATE_FOLDER/$PACK_FILE ];then
	tar -mzxf $UPDATE_FOLDER/$PACK_FILE -C $UPDATE_FOLDER/../app/
fi

if [ -f $UPDATE_FOLDER/$UPDATE_FILE ];then
	if [[ -d $UPDATE_FOLDER/../log ]]; then
		rm -rf $UPDATE_FOLDER/../log/*
	else
		mkdir $UPDATE_FOLDER/../log
	fi
	if [[ -d $UPDATE_FOLDER/../tools ]]; then
		rm -rf $UPDATE_FOLDER/../tools
	fi
	
	echo "  update file is exist"
	/bin/bash $LOCAL_FILE/update_log.sh "[update.sh       ]update file is exist:"
	cd $UPDATE_FOLDER
	tar -mzxvf $UPDATE_FILE >> $UPDATE_LOG_FILE
	rm $UPDATE_FILE
	
	
	# check every file'md5 value
	cd $UPDATE_FOLDER
	if [ -s md5.txt ];then
		for i in `ls`
		do
			exist_msg=`grep $i md5.txt -w`
			if [ "$i" != "md5.txt" ];then 
				if [[ -n "$exist_msg" ]];then
					echo "find $i in md5.txt"
				else
					echo "lost $i md5 value"
					rm -rf *
					exit
				fi
			fi
		done
		#check md5
		ERROR_MESSAGE=`md5sum -c md5.txt | grep -w 'FAILED'`
		WARNING_MESSAGE=`md5sum -c md5.txt | grep -w 'WARNING'`
		if [ -n "$ERROR_MESSAGE" ] || [ -n "$WARNING_MESSAGE" ];then
			echo "$ERROR_MESSAGE"
			echo "$WARNING_MESSAGE"
			/bin/bash $LOCAL_FILE/update_log.sh $UPDATE_LOG_FILE
			echo "  update file md5sum check error"
			/bin/bash $LOCAL_FILE/update_log.sh "[update.sh       ]md5sum check error"
			echo "clear tftpboot folder"
			rm -rf *
			exit
		fi
		if [ ! -d $LOCAL_FILE ];then
			tar -mzxf $UPDATE_FOLDER/$PACK_FILE -C $UPDATE_FOLDER/../app/
		fi

		echo "  update file check  \"md5.txt\" file"
	else
		echo "  update file not have \"md5.txt\" file  or \"md5.txt\" is empty"
		/bin/bash $LOCAL_FILE/update_log.sh "[update.sh       ]update file not have \"md5.txt\" file"
		rm -rf *
		exit
	fi
	
	if [ -f tools.tar.gz ];then
		echo "  update file exist tools files, tar tools in /opt/seeing/ "
		/bin/bash $LOCAL_FILE/update_log.sh "[update.sh       ]update file exist tools files, tar tools in /opt/seeing/ "
		tar -mzxvf  tools.tar.gz -C  /opt/seeing/
	fi
	
	echo "  update file start update ... "
	/bin/bash $LOCAL_FILE/update_log.sh "[update.sh       ]update file start update ... "

	#execute all the .sh file of folder
	for filename in $(ls $LOCAL_FILE/update  | grep ".sh")
	do
		/bin/bash $LOCAL_FILE/update/$filename $UPDATE_FOLDER
		if [ $? -eq 0 ]; then
			echo "  execut $filename success"
			/bin/bash $LOCAL_FILE/update_log.sh "[update.sh       ]execut $filename success"
		else
			echo "  execut $filename error"
			/bin/bash $LOCAL_FILE/update_log.sh "[update.sh       ]execut $filename error"
			cd $UPDATE_FOLDER
			rm -rf *
			exit 1
		fi
	done
	
	echo 'Xavier update rootfs'
	/bin/bash $LOCAL_FILE/update/update_rootfs $UPDATE_FOLDER
	echo "Xavier update end"
	/bin/bash $LOCAL_FILE/update_log.sh "[update.sh       ]Xavier update end "
	cd $UPDATE_FOLDER
	/bin/bash $LOCAL_FILE/update/update_version $UPDATE_FOLDER
	
	rm *  -rf
	sleep 1
	reboot
else

	cd $UPDATE_FOLDER
	rm *  -rf
	echo "  update file is not exist"
fi


