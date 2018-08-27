#########################################################################
# File Name: update_log.sh
# Author: zhen
# mail: qingzhen.zhu@gzseeing.com 
# Created Time: 2017年01月17日 星期二 11时36分40秒
#########################################################################
#!/bin/bash

LOG_FOLDER=/opt/seeing/log/
LOG_FILE=/opt/seeing/log/update.log

if [[ ! -d $LOG_FOLDER ]]; then
		mdkir $LOG_FOLDER -p
fi

if [ $# -lt 1 ]; then
	echo "input param less then 1"
	echo "USAGE: $0 [\"message\"]"

	echo "	EXAMPLE: $0 \"message\""
	exit
fi
UP_DATA_MSG=$1
echo $UP_DATA_MSG >> $LOG_FILE

