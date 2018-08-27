
#########################################################################
# File Name: debugb.sh
# Author: zhen
# mail: zhshwdyx@126.com
# Created Time: 2016年09月24日 星期六 16时48分50秒
#########################################################################
#!/bin/bash

#print the param list as string
#echo $*
#get the number of the params
#num=$#
#get the list of the params
#echo $@

#remote system param
REMOTE_IP=$1
USER=root
REMOTE_FILE=/opt/seeing/app

#local system Source file path
LOCAL_FILE=$(cd "$(dirname "$0")";pwd)
PROJECT_FOLDER=$LOCAL_FILE/..
STORAGE_FOLDER=$PROJECT_FOLDER/build/app
PROJECT_NAME=""

PACK_FILE=seeing.tar.gz

# python will be come two part:
#	one put to the folder of Python 
#	the other part put to handles of remote system

Usage()
{
	cat <<EOF
	USAGE: 
	/bin/bash $0 <ipaddr> <project_name> [cmd]
	ipaddr: zynq ip. eg: 192.168.99.4
	project_name: eg: N131
	cmd:  pack | update | run

	eg: /bin/bash $0 192.168.99.4 N131
	it will send app codes to xavier board. exclude uImgae fpga.bit BOOT.bin and rootfs.

EOF
}

pack_project(){
	echo "pack the process"
	[ ! -d $PROJECT_FOLDER/projects/$PROJECT_NAME ] && echo "Not have this project: $PROJECT_NAME" && exit
	cd $PROJECT_FOLDER
	/bin/bash $PROJECT_FOLDER/scripts/pack.sh $PROJECT_NAME $STORAGE_FOLDER 
}

update_project(){
	echo "update the process"

	# 将打包好的的文件 pack.tar 和 在目标板上运行的脚本 放到目标板的目录下
	cd $STORAGE_FOLDER
	if [  -f $STORAGE_FOLDER/$PACK_FILE ]; then
		scp $STORAGE_FOLDER/$PACK_FILE $LOCAL_FILE/arm_run.sh $USER@$REMOTE_IP:$REMOTE_FILE
#		rm $PACK_FILE 
	else 
		echo "not have the source file, plese pack first !!!"
	fi
}

run_project() {
	echo "run the debug process"
	# set env
	ssh -o StrictHostKeyChecking=no $USER@$REMOTE_IP sh $REMOTE_FILE/arm_run.sh
#	ssh $USER@$REMOTE_IP 
}

if test $# -lt 2 || test $1 = "?" || test $1 = "h" || test $1 = "help" || test $1 = "-H" || test $1 = "-h" || test $1 = "-help" ;then 
	Usage
	exit
	
elif [ $# -ge 3 ]; then
	PROJECT_NAME=$2
	cmd_param=$3
	echo $cmd_param
	if [ $cmd_param = "pack" ];then
		pack_project 
	elif [ $cmd_param = "update" ];then
		update_project
	elif [ $cmd_param = "run" ];then
		run_project
	fi

elif [ $# -ge 2 ]; then
	echo "the param less then 2"
	PROJECT_NAME=$2
	pack_project
	update_project
	run_project
	exit
fi

echo "--------------------$0 end--------------------"
