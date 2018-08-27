#########################################################################
# File Name: pack.sh
# Author: zhen
# mail: qingzhen.zhu@gzseeing.com 
# Created Time: 2016年10月01日 星期六 18时24分33秒
# modify Author:weizhenhua
# mail: zhenhua.wei@gzseeing.com
# modify time: 2017年8月31日 星期四 14时07分3秒
#########################################################################
#!/bin/bash

#print the param list as string
#echo $*
#get the number of the params
#num=$#
#get the list of the params
#echo $@

#local system Source file path
LOCAL_FILE=$(cd "$(dirname "$0")";pwd)
PROJECT_FOLDER=$LOCAL_FILE/..
STORAGE_FOLDER=$PROJECT_FOLDER/app
PROJECT_NAME=""
BLACKLIST_FILE=""

PACK_FILE=seeing.tar.gz
LIB_FILE=libsg*.tar.gz
ZMQ_FILE=zmq*.tar.gz

HARDWARE_JSON=Hardware_Function_Profile.json
MONITOR_JSON=monitor.json
APP_SH=app.sh


make_project_folder(){
    if [ ! -d $STORAGE_FOLDER ]; then
        mkdir -p $STORAGE_FOLDER
    fi

    rm -rf $STORAGE_FOLDER/*
    mkdir $STORAGE_FOLDER/scripts
    mkdir -p $STORAGE_FOLDER/bin
    mkdir -p $STORAGE_FOLDER/../packages

}

add_blacklist(){
    BLACKLIST_FILE+=" $1"
}


merge_monitor_json(){
    echo "#/bin/sh" > $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "\"\"\"exec\" python -E \"\$0\" \"\$@\" \"\"\"#$magic\"" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "import os,sys,json,collections" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "def read_note_str(path):" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    json_text = \"\"" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    note_str=\"\"" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    monitor_json=collections.OrderedDict()" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    comment_area = False" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    with open(path) as jsonfile:" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "        comment_area1 = False" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "        comment_area2 = False" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "        for line in jsonfile.readlines():" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "            if (line.strip()[:3] == \"'''\") and (comment_area1 == False) and (comment_area2 == False):" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                comment_area1 = True" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                note_str= note_str + line" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                continue" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "            elif (line.strip()[:3] == \"'''\") and (comment_area1 == True) and (comment_area2 == False):" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                comment_area1 = False" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                note_str= note_str + line" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                continue" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "            elif (line.strip()[:3] == \"\\\"\\\"\\\"\") and (comment_area1 == False) and (comment_area2 == False):" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                comment_area2 = True" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                note_str= note_str + line" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                continue" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "            elif (line.strip()[:3] == \"\\\"\\\"\\\"\") and (comment_area1 == False) and (comment_area2 == True):" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                comment_area2 = False" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                note_str= note_str + line" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                continue" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "            elif (comment_area1 == True) or (comment_area2 == True):" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                note_str= note_str + line" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "                continue" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "            elif (line.strip()[:1] == \"#\"):" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "               note_str= note_str + line" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "               continue" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "            json_text = json_text + line.strip()" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "        monitor_json = json.loads(json_text, object_pairs_hook = collections.OrderedDict)" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    note_list = [note_str, monitor_json]" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    return note_list" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "original = read_note_str(sys.path[0]+\"/app/monitor/monitor.json\")" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "user = read_note_str(sys.path[0]+\"/monitor_pack.json\")" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "for key, value in user[1].items():" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    original[1][key] = value" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "monitor_json_str = json.dumps(original[1],indent=4)" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "with open(sys.path[0]+\"/app/monitor/monitor.json\",\"w+\") as fp:" >> $STORAGE_FOLDER/../merge_monitor_json.sh
    echo "    fp.write(original[0] + monitor_json_str)" >> $STORAGE_FOLDER/../merge_monitor_json.sh

}

pack_project(){
    echo "pack the process"
    cd $PROJECT_FOLDER    

    cp -rf $PROJECT_FOLDER/packages               $STORAGE_FOLDER/
    rm -rf $STORAGE_FOLDER/packages/devicetree_v1.1.0
	rm -rf $STORAGE_FOLDER/packages/boot_v1.0.0
    cp -rf $PROJECT_FOLDER/command              $STORAGE_FOLDER/
    cp -rf $PROJECT_FOLDER/ee                          $STORAGE_FOLDER/
    rm -rf $STORAGE_FOLDER/ee/board
    cp -rf $PROJECT_FOLDER/daq                        $STORAGE_FOLDER/
    cp -rf $PROJECT_FOLDER/monitor                 $STORAGE_FOLDER/
    cp -rf $PROJECT_FOLDER/logupload                 $STORAGE_FOLDER/
    cp -rf $PROJECT_FOLDER/dut_debugger        $STORAGE_FOLDER/
    cd $PROJECT_FOLDER/scripts
    echo "parse.................................."
    echo $PROJECT_FOLDER/scripts
    ./parse_board_profile  $PROJECT_FOLDER $STORAGE_FOLDER $PROJECT_NAME
    if [ ! $? = 0 ];then
        echo "can't run python scripts"
        exit 0
    fi
    cp -rf $PROJECT_FOLDER/ee/board/programmer                        $STORAGE_FOLDER/ee/board/programmer
    cd $PROJECT_FOLDER
    rm -rf $STORAGE_FOLDER/packages/devicetree_v*
    rm -rf $STORAGE_FOLDER/packages/boot_v*

    cp -rf $PROJECT_FOLDER/scripts/*                     $STORAGE_FOLDER/scripts/ 
    cd $STORAGE_FOLDER/scripts/
    rm -rf $BLACKLIST_FILE
    
    cd  $STORAGE_FOLDER/packages
    if [ -f $STORAGE_FOLDER/packages/$LIB_FILE ];then
        tar -mzxf $STORAGE_FOLDER/packages/$LIB_FILE -C $STORAGE_FOLDER
        rm -rf $LIB_FILE
    fi

    rm -rf kernel_modules_*.tar.gz
    tar_list_file=`ls`
    for tar_file in $tar_list_file
    do
        if [ -d $tar_file ] 
        then
            continue
        fi
        tar -mzxvf $tar_file -C $STORAGE_FOLDER/../packages/
        if [ -d $STORAGE_FOLDER/../packages/lib ] || [ -d $STORAGE_FOLDER/../packages/bin ];then
            [ -d $STORAGE_FOLDER/../packages/lib/ ] && [ ! "`ls -A $STORAGE_FOLDER/../packages/lib/`" = "" ] \
            && cp -rfd $STORAGE_FOLDER/../packages/lib/* $STORAGE_FOLDER/lib/ 
            
            [ -d $STORAGE_FOLDER/../packages/bin/ ] && [ ! "`ls -A $STORAGE_FOLDER/../packages/bin/`" = "" ] \
            && cp -rfd $STORAGE_FOLDER/../packages/bin/* $STORAGE_FOLDER/bin/ 
        fi
        if [ ! -d $STORAGE_FOLDER/../packages/lib ] && [ ! -d $STORAGE_FOLDER/../packages/lib ];then
            cp -rf $STORAGE_FOLDER/../packages/* $STORAGE_FOLDER/packages/
        fi
        rm -rf $STORAGE_FOLDER/../packages/*
    done
    rm -rf *.gz

    cd $STORAGE_FOLDER/command/handle
    handle_file_list=`ls`
    if [ -n "$handle_file_list" ];then
        for file in $handle_file_list
        do
            [ -d $file ] && [ $file != $PROJECT_NAME ] && rm -rf $file && continue
            [ ! -d $file ] && continue
            [ -d $file ] && [ $file = $PROJECT_NAME ] && echo "" >> ./__init__.py \
            && cat $STORAGE_FOLDER/command/handle/$file/__init__.py >> ./__init__.py \
            && rm $STORAGE_FOLDER/command/handle/$file/__init__.py && mv $STORAGE_FOLDER/command/handle/$file/* ./ 
            
            rm -rf $file && continue
        done
    fi

    cd $PROJECT_FOLDER/projects
    project_file_list=`ls`
    if [ -n "$project_file_list" ];then
        for file in $project_file_list
        do
            [ -d $file ] && [ $file = $PROJECT_NAME ] \
            && cp -rf $PROJECT_FOLDER/projects/$file/$HARDWARE_JSON $STORAGE_FOLDER/ee/profile/ \
            && [ -f $PROJECT_FOLDER/projects/$file/$MONITOR_JSON ] \
            && cp -rf $PROJECT_FOLDER/projects/$file/$MONITOR_JSON $STORAGE_FOLDER/../monitor_pack.json \
            && merge_monitor_json && sh $STORAGE_FOLDER/../merge_monitor_json.sh \

            [ -d $file ] && [ $file = $PROJECT_NAME ] \
            && [ -f $PROJECT_FOLDER/projects/$file/$APP_SH ] \
            && cp -rf $PROJECT_FOLDER/projects/$file/$APP_SH $STORAGE_FOLDER/scripts/

            if [ -d $file ] && [ $file = $PROJECT_NAME ];then
                cd $PROJECT_FOLDER/projects/$file/ 
                FOLDER=`ls $PROJECT_FOLDER/projects/$file/`
                if [ -n "$FOLDER" ];then
                    for folder_file in $FOLDER
                    do
                        [ -d $folder_file ] && cp -rf $folder_file $STORAGE_FOLDER/ 
                        if [[ "$folder_file" =~ "rootfs" ]];then
                            continue
                        fi
                        if [[ "$folder_file" =~ ".gz" ]];then
                            tar -mzxvf $PROJECT_FOLDER/projects/$file/$folder_file -C $STORAGE_FOLDER/../packages/
                            if [ -d $STORAGE_FOLDER/../packages/lib ] || [ -d $STORAGE_FOLDER/../packages/bin ];then
                                [ -d $STORAGE_FOLDER/../packages/lib/ ] && [ ! "`ls -A $STORAGE_FOLDER/../packages/lib/`" = "" ] \
                                && cp -rfd $STORAGE_FOLDER/../packages/lib/* $STORAGE_FOLDER/lib/ 
                                
                                [ -d $STORAGE_FOLDER/../packages/bin/ ] && [ ! "`ls -A $STORAGE_FOLDER/../packages/bin/`" = "" ] \
                                && cp -rfd $STORAGE_FOLDER/../packages/bin/* $STORAGE_FOLDER/bin/ 

                            fi
                            if [ ! -d $STORAGE_FOLDER/../packages/lib ] && [ ! -d $STORAGE_FOLDER/../packages/lib ];then
                                cp -rfd $STORAGE_FOLDER/../packages/* $STORAGE_FOLDER/packages/

                            fi
                            rm -rf $STORAGE_FOLDER/../packages/*

                        fi
                    done
                fi
                cd -
            fi
        done
    fi

}

echo "--------------------$0 --------------------"
add_blacklist       arm_run.sh
add_blacklist       deploy.sh
add_blacklist       pack.sh
add_blacklist       release.sh

if [ $# -ge 2 ]; then
    PROJECT_NAME=$1
    STORAGE_FOLDER=$2
    make_project_folder
    cd $PROJECT_FOLDER

    pack_project

    cd $STORAGE_FOLDER
    tar --exclude *.pyc -zcvf $PACK_FILE *
    #tar -zcvf  $PACK_FILE *
elif [ $# -ge 1 ]; then
    PROJECT_NAME=$1
    echo "use default folder"
    make_project_folder
    pack_project
    cd $STORAGE_FOLDER
    tar --exclude *.pyc -zcvf $PACK_FILE *
    #tar -zcvf  $PACK_FILE *
else
    echo "Usage:"
    echo "  $0 <project_name>"
    echo ""
fi
echo "--------------------$0  end--------------------"

