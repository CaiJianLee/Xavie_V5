#-*- coding: UTF-8 -*-
__author__ = 'jk'

import re
import time
import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger
from dut_debugger.programmer.dfucommon import dfu_common
from dut_debugger.programmer.chipprog.chipprog import ChipProg
from dut_debugger.programmer.chipprog.cortexmprog import CortexMProg



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
        
        params["write_array"] = sequence_arr
        params["length"] = len(sequence_arr)
        
        #configure start csw register
        params["value"] = 0x23000002
        
        response = self.rpc_client_node.call("ConfigureSwitchSequence",**params)
        # # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
            
        response = self.rpc_client_node.call("ConfigureCswData",**params)
        # # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)

        return dfu_common.get_correct_return_state(response)













