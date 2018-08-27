#-*- coding: UTF-8 -*-
__author__ = 'jk'
 
import re
import time
# import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger


RETURN_TYPE = {
    "JSON_STRING":0,
    "JSON_BOOLEAN":1,
    "JSON_INTEGER":2,
    "JSON_REAL":3,
    "JSON_OBJECT":4,
    "JSON_ARRAY":5,
    "NULL":255,
    }
def return_type(type_str):
    return RETURN_TYPE[type_str]


def get_driver_type_support(rpc_client_node):
    args = {}
    dfu_driver_type = rpc_client_node.call("GetSupportDriverType",**args)
    return dfu_driver_type

def get_protocol_type_support(rpc_client_node):
    args = {}
    dfu_protocol_type = rpc_client_node.call("GetSupportProtocolType",**args)
    return dfu_protocol_type

def get_chip_arch_type_support(rpc_client_node):
    args = {}
    dfu_chip_arch_type = rpc_client_node.call("GetSupportChipArchitectureType",**args)
    return dfu_chip_arch_type

def get_chip_type_support(rpc_client_node,arch_type):
    args = {"arch_type":arch_type}
    dfu_chip_type = rpc_client_node.call("GetSupportChipType",**args)
    return dfu_chip_type 

def get_error_return_state(response):
    #True,str,return_str
    ret_str = "-------------error--------------\r\n"
    if return_type("JSON_STRING") == return_type(response["return_type"]):
        ret_str += response["return"]
    elif return_type("JSON_BOOLEAN") == return_type(response["return_type"]):
        ret_str += str(response["return"])
    elif return_type("JSON_INTEGER") == return_type(response["return_type"]):
        ret_str += str(response["return"])
    elif return_type("JSON_REAL") == return_type(response["return_type"]):
        ret_str += str(response["return"])
    elif return_type("NULL") == return_type(response["return_type"]):
        ret = str(response["return"])
    elif return_type("JSON_ARRAY") == return_type(response["return_type"]):
        for i in range(response["return_size"]):
            ret_str += "0x%x"%(response["return"][i])
            if i < response["return_size"]-2:
                ret_str += ","
        # ret_str += ".\r\n"
    else:
        ret_str += "not this return type"
    ret_str += response["state_description"]+"-----"+"status = "+str(response["state"])+".\r\n"

#     logger.info(str(response["logger_info"]))
    return False,"JSON_STRING",ret_str


def get_correct_return_state(response):
    #True,type,return
    ret = ""
    if return_type("JSON_STRING") == return_type(response["return_type"]):
        ret = response["return"]
    elif return_type("JSON_BOOLEAN") == return_type(response["return_type"]):
        ret = response["return"]
    elif return_type("JSON_INTEGER") == return_type(response["return_type"]):
        ret = response["return"]
    elif return_type("JSON_REAL") == return_type(response["return_type"]):
        ret = response["return"]
    elif return_type("JSON_ARRAY") == return_type(response["return_type"]):
        ret = response["return"]
    elif return_type("NULL") == return_type(response["return_type"]):
        ret = str(response["return"])
    else:
        ret += "not this return type"
    # ret += response["state_description"]+"-----"+"status = "+str(response["state"])+".\r\n"

#     logger.info(str(response["logger_info"]))
    return True,response["return_type"],ret

