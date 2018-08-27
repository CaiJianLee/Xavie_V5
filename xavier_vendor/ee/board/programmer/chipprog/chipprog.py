#-*- coding: UTF-8 -*-
# from usbcreator.backends.base.backend import abstract
__author__ = 'jk'

import re
import time
# import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger
from ee.board.programmer.dfucommon import dfu_common


class ChipProg():
    def __init__(self,rpc_client_node):
        self.rpc_client_node = rpc_client_node
        if self.rpc_client_node == False:
            # pring("rpc client is not exist!")
            logger.error("rpc client is not exist!")
        pass
    
#     @abstract
    def create_instance(self,dev_path,what_chip):
        "in :                    \
           dev_path:string"
        return False
    
    def destroy_instance(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        params = {}
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("DfuProgInstanceDestroy",**params)
        # # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)#response["state_description"],response["state"]
        return dfu_common.get_correct_return_state(response)#response["return"]
    
    def instance_initial(self,freqency_hz,instance_sequence = 0):
        "in:\
            frequency_hz:unsigned int\
            instance_sequence:unsigned int"
        params = {}
        params["frequency_hz"] = freqency_hz
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("DriverInitial",**params)
        # # pring(response)
        if response["state"] < 0:
            return dfu_common.get_error_return_state(response)
        response = self.rpc_client_node.call("SetFrequencyHz",**params)
        # # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
    
    def set_frequency(self,freqency_hz,instance_sequence = 0):
        "in:\
            frequency_hz:unsigned int\
            instance_sequence:unsigned int"
        params = {}
        params["frequency_hz"] = freqency_hz
        params["instance_sequence"] =instance_sequence
        response = self.rpc_client_node.call("SetFrequencyHz",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
    
    def get_frequency(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        params = {}
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("ReadFrequencyHz",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
    
    def dut_initial(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        params = {}
        params["instance_sequence"] = instance_sequence
        
        response = self.rpc_client_node.call("DutInitial",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
    
    def dut_exit(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        params = {}
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("DutExit",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
    
    def dut_storage_infusing(self,target_file_name,target_address,file_offset,size,instance_sequence = 0):
        "in:\
            target_file_name:str,the file path\
            target_address: unsigned int,the DUT target infusing address\
            file_offset:unsigned int,loading the firmware file start address\
            size:unsigned int,program size\
            instance_sequence:unsigned int\
            "
        params = {}
        params["target_file_name"] = target_file_name
        params["target_address"] = target_address
        params["file_offset"] = file_offset
        params["size"] = size
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("DutStorageInfusing",**params)
        # pring(response)
        if response["state"] < 0:
            logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
    
    def dut_storage_checkout(self,target_file_name,target_address,file_offset,size,instance_sequence = 0):
        "in:\
            target_file_name:str,the file path\
            target_address: unsigned int,the DUT target checkout address\
            file_offset:unsigned int,loading the firmware file start address\
            size:unsigned int,program size\
            instance_sequence:unsigned int\
            "
        params = {}
        params["target_file_name"] = target_file_name
        params["target_address"] =target_address
        params["file_offset"] =file_offset
        params["size"] =size
        params["instance_sequence"] =instance_sequence
        response = self.rpc_client_node.call("DutStorageCheckout",**params)
        # pring(response)
        if response["state"] < 0:
            logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
        
    def dut_storage_reading(self,target_file_name,target_address,size,instance_sequence = 0):
        "in:\
            target_file_name:str,the file path\
            target_address: unsigned int,the DUT target checkout address\
            size:unsigned int,program size\
            instance_sequence:unsigned int\
            "
        params = {}
        params["target_file_name"] =arget_file_name
        params["target_address"] =target_address
        params["size"] =size
        params["instance_sequence"] =instance_sequence
        response = self.rpc_client_node.call("DutStorageReading",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)

    def dut_storage_erase(self,instance_sequence,target_address= None,size= None):
        "in:\
            instance_sequence:unsigned int\
            "
        params = {}
        params["instance_sequence"] =instance_sequence
        if target_address != None and size != None:
            params["target_address"] =target_address
            params["size"] =size
        response = self.rpc_client_node.call("DutStorageErase",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
#--------------------------------function for swd cortexM-------------------------------------
    def dut_reg_read(self,address,instance_sequence = 0):
        "in:\
            address:unsigned int ,read target address\
            instance_sequence:unsigned int\
            "
        params = {}
        params["address"] =address
        params["instance_sequence"] =instance_sequence
        response = self.rpc_client_node.call("RegRead",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)

    def dut_reg_write(self,address,value,instance_sequence = 0):
        "in:\
            address:unsigned int ,read target address\
            value:unsigned int ,write target data\
            instance_sequence:unsigned int\
            "
        params = {}
        params["address"] =address
        params["value"] =value
        params["instance_sequence"] =instance_sequence
        response = self.rpc_client_node.call("RegRead",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
    
    def dut_reset(self,pluse_delay_us = 10000,instance_sequence = 0):
        "in:\
            pluse_delay_us:unsigned int ,read target address\
            instance_sequence:unsigned int\
            "
        params = {}
        params["pluse_delay_us"] = pluse_delay_us
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("Reset",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
#--------------------------------function for spi flash-------------------------------------
    def flash_interactive(self,cmd,address,dummy_data_num,write_array,length,instance_sequence = 0):
        "in:\
            cmd:unsigned int ,spi flash command\
            address:unsigned int\
            dummy_data_num:unsigned int\
            write_array:array\
            length:unsigned int ,array length not more than 512\
            instance_sequence:unsigned int\
            "
        params = {}
        params["cmd"] = cmd,
        params["address"] = address,
        params["dummy_data_num"] = dummy_data_num,
        params["write_array"] = write_array,
        params["length"] = length,
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("FlashInteractive",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)

    def flash_enter_32_bit_mode(self):
        "in:\
            instance_sequence:unsigned int\
            "
        params = {}
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("Enter32BitAddressMode",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)

    def flash_exit_32_bit_mode(self):
        "in:\
            instance_sequence:unsigned int\
            "
        params = {}
        params["instance_sequence"] = instance_sequence
        response = self.rpc_client_node.call("Exit32BitAddressMode",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)

