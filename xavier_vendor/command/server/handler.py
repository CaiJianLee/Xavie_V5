#-*- coding: UTF-8 -*-
import sys
import os
import importlib
import traceback
from command.handle import *
import json
import command.server.handle_utility as utility
from ee.common import logger

global CMD_LIST
CMD_LIST = {}

def call_handle(*params):
    # deal params
    handle_params = list(params)
    #print(handle_params)
    del handle_params[0]

    # get cmd list 
    cmd_list = get_cmd_list()
    #
    logger.info("enter command")
    #
    # print cmd_list
    # doing
    if params[0] in cmd_list :
        #
        logger.info(str(params[0]))
        logger.info(str(handle_params))
        #
        try:
            if handle_params[0]:
                result = cmd_list[params[0]](handle_params[0].split(','))
            else:
                result = cmd_list[params[0]](handle_params[0])
            #
            logger.info(str(result)+"params[0]")
            #
        except Exception as e:
            result = utility.handle_error(utility.handle_errorno['handle_errno_call_handle_exception'],"call handle exception")
            logger.info("call_handle Exception : %s"%(traceback.format_exc()))
    else :
        result = utility.handle_error(utility.handle_errorno['handle_errno_not_have_this_command'],"not have this command")
        #
        logger.info(str(result)+"result error")
        #
        #
    logger.info("exit command")
    #
    if not result:
        result = ""
    return result

def get_cmd_list():
    global CMD_LIST
    if not CMD_LIST:
        __cmd_list_init()
    return CMD_LIST

def __append_cmd(cmd_message):
    global CMD_LIST
    try:
        CMD_LIST[cmd_message["cmd"]] = getattr(eval(cmd_message["module"]), cmd_message["handle"])
    except Exception:
        logger.boot("%s have not handle"%(cmd_message["cmd"]))
    return

def __cmd_list_init():
    global CMD_LIST
    CMD_LIST.clear()
  #  print("----- init cmd list -----")
    try:
        if True == os.path.exists(os.path.dirname(sys.argv[0]) + "/handles_config.json"):
            json_file = '%s/handles_config.json'%(os.path.dirname(sys.argv[0]))
        else:
            json_file = '%s/command/handle/handles_config.json'%(os.environ.get("PYTHON_HOME", "/opt/seeing/app"))
        handles_file = open(json_file)
    except Exception as e:
        logger.error("open handles config file error !!!")
        return
    for each_line in handles_file :
        line = each_line.strip()
        line = line.strip(',')
        msg = None
        try:
            msg = json.loads(line)
        except Exception as e:
            continue
        __append_cmd(msg)

    logger.boot("cmd list is :" + str(CMD_LIST))
    handles_file.close()
    return

#第一次加载模块，需要初始化指令列表
def handle_init():
    __cmd_list_init()
    system.get_fpga_version()

	#end of the handle fi le
