#!/bin/bash


cd `pwd`/../
XAVIER_PRJ_PATH=`pwd`
echo "project path is $XAVIER_PRJ_PATH" 
export PYTHONPATH=$XAVIER_PRJ_PATH:$XAVIER_PRJ_PATH/ee
pytest --cov=$XAVIER_PRJ_PATH tests/$1

