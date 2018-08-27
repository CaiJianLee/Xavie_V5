#-*- coding: UTF-8 -*-
__author__ = 'jk'

import re
import time
# import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger
from ee.board.programmer.dfucommon import dfu_common
from ee.board.programmer.chipprog.chipprog import ChipProg
from ee.board.programmer.chipprog.cortexmprog import CortexMProg



hearst_sequence1 = 0xE79E
hearst_sequence2 = 0xEDB6


class HearstProg(CortexMProg):
    def __init__(self,rpc_client_node):
        CortexMProg.__init__(self,rpc_client_node)
        
    @staticmethod
    def chip_type_name(self):
        return "hearst"
    
    def instance_initial(self,freqency_hz,instance_sequence = 0):
        "in:\
            frequency_hz:unsigned int\
            instance_sequence:unsigned int\
            "
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
        
        #configure switch sequence
        sequence_arr = [0xff for i in range(8)]
        sequence_arr += [hearst_sequence1&0xFF,(hearst_sequence1>>8)&0xFF]
        sequence_arr += [0xff for i in range(8)]
        sequence_arr += [hearst_sequence2&0xFF,(hearst_sequence2>>8)&0xFF]
        sequence_arr += [0xff for i in range(8)]
        sequence_arr += [0x00 for i in range(2)]
        
        #configure switch sequence
        logger.warning("configuring the switch sequence")
        params["write_array"] = sequence_arr
        params["length"] = len(sequence_arr)
        response = self.rpc_client_node.call("ConfigureSwitchSequence",**params)
        logger.warning(str(params["write_array"]))
        # # print(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        #configure start csw register
        logger.warning("configuring the CSW data")
        params["value"] = 0x23000002
        response = self.rpc_client_node.call("ConfigureCswData",**params)
        if response["state"] < 0:
            return dfu_common.get_error_return_state(response)
        #configure reset  
        params["pluse_delay_us"] = -1
        response = self.rpc_client_node.call("ConfigureResetDelay",**params)
        if response["state"] < 0:
            return dfu_common.get_error_return_state(response)
        
        return dfu_common.get_correct_return_state(response)

    def dut_initial(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        params = {}
        params["instance_sequence"] = instance_sequence
        params["hearst_dut"] = 0
        
        response = self.rpc_client_node.call("DutExit",**params)
        # pring(response)
        if response["state"] < 0:
            return dfu_common.get_error_return_state(response)
        response = self.rpc_client_node.call("DutInitial",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        
        #halt the system
        params["address"] = 0xE000EDF0
        params["value"] = 0xA05F0003
        response2 = self.rpc_client_node.call("RegWrite",**params)
        if response2["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response2)
        logger.warning(response2["return"])
        #read system state
        response2 = self.rpc_client_node.call("RegRead",**params)
        if response2["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response2)
        logger.warning(response2["return"])
        
        return dfu_common.get_correct_return_state(response)    
    
    def dut_exit(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        params = {}
        params["instance_sequence"] = instance_sequence
#         response = self.rpc_client_node.call("DutExit",**params)
#         # pring(response)
#         if response["state"] < 0:
#             return dfu_common.get_error_return_state(response)
        
        #soft reset the cortexm system
        params["address"] = 0xE000EDF0
        params["value"] = 0xA05F0000
        response2 = self.rpc_client_node.call("RegWrite",**params)
        if response2["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response2)
        
        params["address"] = 0xE000ED0C
        params["value"] = 0x05FA0004
        response2 = self.rpc_client_node.call("RegWrite",**params)
        if response2["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response2)
        # response = self.rpc_client_node.call("DutExit",**params)
        # # pring(response)
        # if response["state"] < 0:
        #     return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response2)

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
        #------abort?
        
        #-------
        params["address"] = 0x44443044
        params["value"] = 0x01
        response = self.rpc_client_node.call("RegWrite",**params)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        
        params["address"] = 0x440090C4
        params["value"] = 0x0071C030
        response = self.rpc_client_node.call("RegWrite",**params)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)

        params["address"] = 0x440090C8
        params["value"] = 0x0071C030
        response = self.rpc_client_node.call("RegWrite",**params)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        
        params["address"] = 0x440090CC
        params["value"] = 0x0071C030
        response = self.rpc_client_node.call("RegWrite",**params)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        params["address"] = 0x440090D0
        params["value"] = 0x0071C030
        response = self.rpc_client_node.call("RegWrite",**params)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)

        params["address"] = 0x440090D4
        params["value"] = 0x0075C001
        response = self.rpc_client_node.call("RegWrite",**params)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        
        params["address"] = 0x440090D8
        params["value"] = 0x0075C001
        response = self.rpc_client_node.call("RegWrite",**params)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        
        return dfu_common.get_correct_return_state(response)

















