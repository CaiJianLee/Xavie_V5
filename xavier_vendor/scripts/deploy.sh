#########################################################################
# File Name: deploy.sh:
# Author: zhangye
# mail: zhangye@gzseeing.com 
# Created Time: 2018年3月26日 星期一 11时00分22秒
# History: compile devicetree and Boot.bin on Xavier when packed a project
# Author: zhen
# mail: qingzhen.zhu@gzseeing.com 
# Created Time: 2016年12月23日 星期五 09时32分22秒
# modify Author:weizhenhua
# mail: zhenhua.wei@gzseeing.com
# modify time: 2017年8月31日 星期四 14时07分3秒
# Author: zuogui
# mail: zuogui.yang@gzseeing.com
# Created Time: 2018年4月12日 星期四 18时06分17秒
# History: add --remote option to upload packeges to remote
#########################################################################
#!/bin/bash

BOARD_NAME=ARM_Board_D3

LOCAL_FILE=$(cd "$(dirname "$0")";pwd)
PROJECT_NAME=""
RENAME=

SYSTEM_TYPE=`uname`

SOURCE_FILE=$LOCAL_FILE/../
OUTPUT_PATH=$SOURCE_FILE

FLODER=$LOCAL_FILE/../build/deploy/


USER=root
REMOTE_FILE=/opt/seeing/tftpboot
PASSWORD=123456


Usage()
{
	project_name=`ls $SOURCE_FILE/projects/`
	cat <<EOF
	Usage:
	$0 <version num> <project_name> --exclude [file] --include [file] --remote [ip addr]
	project_name: specific project name: 
$project_name
	version num: project name version
	file: BOOT.bin | devicetree.dtb | fpga.bit | uImage | rootfs.tar.gz | tools
	dir:  the output dir, default is build/deploy
	the package default include BOOT.bin, devicetree.dtb, fpga.bit and uImage
	if want to pack tools in tar,eg: /bin/bash $0 v5.00.01 N131_FCT_IA --include tools
	if want to clean project.eg: /bin/bash $0 clean
	if want to upload the packeges && update automatically, eg: /bin/bash $0 v5.00.01 N131_FCT_IA --remote 192.168.99.11
	eg: /bin/bash $0 v5.00.01 N131_FCT_IA"
EOF
}

clean_project()
{
	echo "clean project ..."
	rm -rf $SOURCE_FILE/build 
	rm -rf ARM_Board_D3_*
	echo "clean project ok."
	exit 1
}


build_boot_and_devicetree()
{
    cd $FLODER
    #add project with amp and produce boot.bin and device.dtb
    if [ -f $SOURCE_FILE/projects/$PROJECT_NAME/FSBL*.elf ];then
        if [ -f BOOT.bin ];then
            rm BOOT.bin
        fi
        cp -rf $SOURCE_FILE/packages/boot_v*/* ./
        if [ $? -ne 0 ];then
            echo "Can not find $SOURCE_FILE/packages/boot_v* package exit !"
            exit 1
        fi
        /bin/bash build.sh
        rm boot.bif bootgen FSBL.elf u-boot.elf build.sh u-boot_xilinx-v2017.4.elf
        rm FSBL*.elf
    fi
    if [ -f $SOURCE_FILE/projects/$PROJECT_NAME/pl*.dtsi ];then
        if [ -f devicetree.dtb ];then
            rm devicetree.dtb
        fi

        cp -rf $SOURCE_FILE/packages/devicetree_v*/* ./
        if [ $? -ne 0 ];then
            echo "Can not find $SOURCE_FILE/packages/devicetree_* package exit !"
            exit 1
        fi
        if [ -d $SOURCE_FILE/projects/$PROJECT_NAME/amp ];then
            /bin/bash build.sh amp
        else
            /bin/bash build.sh
        fi
        rm build.sh skeleton.dtsi system.dts system_amp.dts zynq-7000.dtsi pl.dtsi
        rm pl*.dtsi
    fi


    if [ ! -f BOOT.bin ] || [ ! -f devicetree.dtb ];then
        echo "Please ensure BOOT.bin and devicetree.dtb exist  package exit !"
        exit 1
    fi


    if [ -f fpga_*.bit ];then
        if [ -f fpga.bit ];then
            rm fpga.bit
            mv fpga_*.bit fpga.bit
        else
            mv fpga_*.bit fpga.bit
        fi
    fi

    if [ ! -f fpga.bit ];then
        echo "Please ensure fpga.bit or fpga_*.bit exist  package exit !"
        exit 1
    fi

    cp BOOT.bin $SOURCE_FILE/projects/$PROJECT_NAME/
    cp devicetree.dtb  $SOURCE_FILE/projects/$PROJECT_NAME/
    cp fpga.bit  $SOURCE_FILE/projects/$PROJECT_NAME/
}

if [ "$1" = "clean" ];then
	clean_project
fi

if test $# -lt 2 || test $1 = "?" || test $1 = "h" || test $1 = "help" || test $1 = "-H" || test $1 = "-h" || test $1 = "-help" ;then 
	Usage
	exit 0
fi

version_str=$1
VERSION=${version_str#*v}
VERSION=${VERSION#*V}
echo 'version is :'$VERSION

PROJECT_NAME=$2

[ -d $LOCAL_FILE ]
if [ $? -ne 0 ];then
	echo "[err ] Please check your folder, cannot contain special characters in your folder."
	echo "exit !!!"
	exit 1
fi
[ -d $SOURCE_FILE/projects/$PROJECT_NAME ]
if [ $? -ne 0 ];then
	echo "[err ] Please check your folder, cannot contain special characters in your folder."
	echo "exit !!!"
	exit 1
fi

# get params
param_type='none'
remote_status=0
tools_status=0
for arg in "$@"
do
	if [ $arg = '--include' ];then
		param_type='include'
	elif [ $arg = '--exclude' ];then
		param_type='exclude'
	elif [ $arg = '--output' ];then
		param_type='path'
	elif [ $arg = '--rename' ];then
		param_type='rename'
	elif [ $arg = '--remote' ];then
		param_type='remote'
	else
		if [ $param_type = 'include' ];then
			if [ $arg = 'tools' ];then
				tools_status=1
				echo "include tools file "
			else
				INCLUDE_FILE="$INCLUDE_FILE $arg"	
			fi		
		elif [ $param_type = 'exclude' ];then
			EXCLUDE_FILE="$EXCLUDE_FILE $arg"			
		elif [ $param_type = 'path' ];then
			OUTPUT_PATH=$arg
		elif [ $param_type = 'rename' ];then
			RENAME=$arg
		elif [ $param_type = 'remote' ];then
			REMOTE_IP=$arg
			remote_status=1
		fi
	fi
done
echo $INCLUDE_FILE
echo $EXCLUDE_FILE
echo $OUTPUT_PATH
echo $FLODER

echo 'project name is :'$PROJECT_NAME

if [ ! -d $FLODER ];then
	mkdir -p $FLODER
else
	rm -rf $FLODER/* 
fi


cd $FLODER
/bin/bash $LOCAL_FILE/release.sh 1 $PROJECT_NAME pack 
cp -rf $SOURCE_FILE/projects/$PROJECT_NAME/* ./
echo $SYSTEM_TYPE
if [ $SYSTEM_TYPE = 'Linux' ];then
    build_boot_and_devicetree
else
    rm FSBL*.elf
    rm pl*.dtsi
    mv fpga_*.bit fpga.bit
fi
rm -rf $FLODER/*.json $FLODER/*.xlsx $FLODER/*.gz
cp $FLODER/../app/seeing.tar.gz $FLODER
if [ $? -ne 0 ];then
	echo "Can not find $SOURCE_FILE/build/app/seeing.tar.gz. package exit !"
	exit 1
fi
[ -f $SOURCE_FILE/projects/$PROJECT_NAME/rootfs*.tar.gz ] \
&& cp -rf $SOURCE_FILE/projects/$PROJECT_NAME/rootfs*.tar.gz $FLODER


if [ -f $SOURCE_FILE/projects/$PROJECT_NAME/kernel_modules_*.tar.gz ];then
    tar zxf $SOURCE_FILE/projects/$PROJECT_NAME/kernel_modules_*.tar.gz -C $FLODER
elif [ -d $SOURCE_FILE/projects/$PROJECT_NAME/amp ];then
    tar zxf $SOURCE_FILE/packages/kernel_modules_zynqamp_*.tar.gz -C $FLODER
elif [ -d $SOURCE_FILE/projects/$PROJECT_NAME/pru ];then
    echo ""
else
    tar zxf $SOURCE_FILE/packages/kernel_modules_zynq_*.tar.gz -C $FLODER
fi

firmware_file=`ls`
if [ -n "$firmware_file" ];then
    for folder_file in $firmware_file
    do
        [ -d $folder_file ] && rm -rf $folder_file
    done
fi

cd $FLODER
echo "first list file:"
ls
echo "------------"

if [ -n "$INCLUDE_FILE" ];then
	cd $SOURCE_FILE/bin/
	cp $INCLUDE_FILE $FLODER
	if [ $? -ne 0 ];then
		echo "ERR: cp \"$INCLUDE_FILE\"  error!"
		exit 1
	fi
	cd $FLODER
fi
if [ -n "$EXCLUDE_FILE" ];then
	cd $FLODER
	rm $EXCLUDE_FILE 
	if [ $? -ne 0 ];then
		echo "ERR: rm \"$EXCLUDE_FILE\" error!"
		exit 1
	fi
fi
if [ $tools_status -eq 1 ];then
	echo "tar tools file"
	cd $SOURCE_FILE
	tar zcvf tools.tar.gz tools
	mv tools.tar.gz  $FLODER
fi

cd $FLODER
echo "second list file:"
ls
echo "------------"

if [ ! -f $SOURCE_FILE/projects/$PROJECT_NAME/version.txt ];then
	echo "warn: not have version.txt !!! "
#	exit 1
else
# change seeing param 
	while read line; do
		eval "$line"
	done < version.txt
fi

string=${seeing#=}
project=${project#=}
time_string=${compile_time#=}
if [ -z $string ];then
	echo "not have \"seeing\" value in \"version.txt\" file"
	echo "now version is "$VERSION
	echo "seeing="$VERSION >> version.txt
else
	echo "old version is "$string
	echo "new version is "$VERSION
	sed -i 's/'$string'/'$VERSION'/g' version.txt 2>/dev/null
    if [ $? -ne 0 ];then
        sed -i '' 's/'$string'/'$VERSION'/g' version.txt
    fi
fi

if [ -z $project ];then
	echo "not have \"project\" value in \"version.txt\" file"
	echo "now project is "$PROJECT_NAME
	if [ $RENAME ];then
		echo "project="$RENAME>> version.txt
	else
		echo "project="$PROJECT_NAME>> version.txt
	fi
else
	echo "project name is \""$PROJECT_NAME"\""
	if [ $RENAME ];then
		sed -i 's/'$project'/'$RENAME'/g' version.txt 2>/dev/null
        if [ $? -ne 0 ];then
            sed -i '' 's/'$project'/'$RENAME'/g' version.txt
        fi
	else
		sed -i 's/'$project'/'$PROJECT_NAME'/g' version.txt 2>/dev/null
        if [ $? -ne 0 ];then
            sed -i '' 's/'$project'/'$PROJECT_NAME'/g' version.txt
        fi
	fi
fi

COMPILE_TIME=$(date  +"%Y-%m-%d--%H:%M:%S")
if [ -z $time_string ];then
	echo "not have \"compile_time\" value in \"version.txt\" file"
	echo "now compile time is "$COMPILE_TIME
	echo "compile_time="$COMPILE_TIME>> version.txt
else
	echo "now time is "$COMPILE_TIME
	echo "compile time name is \""$COMPILE_TIME"\""
	sed -i 's/'$time_string'/'$COMPILE_TIME'/g' version.txt 2>/dev/null
    if [ $? -ne 0 ];then
        sed -i '' 's/'$time_string'/'$COMPILE_TIME'/g' version.txt
    fi
fi

sync
if [ -f md5.txt ];then
	rm -rf md5.txt
fi
md5sum * > md5.txt 2>/dev/null
if [ $? -ne 0 ];then
	rm -rf md5.txt
	md5sum * > md5.txt
fi

if [ $RENAME ];then
    echo "Remane project $PROJECT_NAME to $RENAME" 
    SW="$BOARD_NAME"_"$RENAME"
else
    SW="$BOARD_NAME"_"$PROJECT_NAME"
fi
PACK_NAME="$SW"_V"$VERSION".tar.gz
tar -mzcf $PACK_NAME *
mv $PACK_NAME $OUTPUT_PATH

# mv version.txt $SOURCE_FILE/bin/
mv version.txt $SOURCE_FILE/projects/$PROJECT_NAME/

rm -rf $FLODER/build/app/* 

if [ $remote_status -eq 1 ];then
	which "sshpass" > /dev/null
	if [ $? -eq 0 ];then
		sshpass -p $PASSWORD scp $OUTPUT_PATH$PACK_NAME $USER@$REMOTE_IP:$REMOTE_FILE
		sshpass -p $PASSWORD ssh -o StrictHostKeyChecking=no $USER@$REMOTE_IP "sync ; reboot"
	else
		which "expect" > /dev/null
		if [ $? -eq 0 ]; then
			if [ -f "$LOCAL_FILE/expect_scp" -a -f "$LOCAL_FILE/expect_ssh" ];then
				$LOCAL_FILE/expect_scp $REMOTE_IP $USER $PASSWORD $OUTPUT_PATH$PACK_NAME $REMOTE_FILE/$PACK_NAME
				$LOCAL_FILE/expect_ssh $REMOTE_IP $USER $PASSWORD "sync ; reboot"
			else
				scp $OUTPUT_PATH$PACK_NAME $USER@$REMOTE_IP:$REMOTE_FILE
				ssh -o StrictHostKeyChecking=no $USER@$REMOTE_IP "sync ; reboot"
			fi
		else
			scp $OUTPUT_PATH$PACK_NAME $USER@$REMOTE_IP:$REMOTE_FILE
			ssh -o StrictHostKeyChecking=no $USER@$REMOTE_IP "sync ; reboot"
		fi
	fi
fi


