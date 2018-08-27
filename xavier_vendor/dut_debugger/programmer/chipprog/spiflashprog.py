#-*- coding: UTF-8 -*-
__author__ = 'jk'

import re
import time
import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger
from dut_debugger.programmer.dfucommon import dfu_common
from dut_debugger.programmer.chipprog.chipprog import ChipProg

class SpiFlash(ChipProg):
    def __init__(self,rpc_client_node):
        ChipProg.__init__(self,rpc_client_node)
    
    def create_instance(self,dev_path,what_chip):
        "in :                    \
           dev_path:string"
        protocol_type = dfu_common.get_protocol_type_support(self.rpc_client_node)["spi"]
        arch_type = dfu_common.get_chip_arch_type_support(self.rpc_client_node)["spiflash"]
        chip_type = dfu_common.get_chip_type_support(self.rpc_client_node,arch_type)[what_chip]
        
        logger.info(dfu_common.get_protocol_type_support(self.rpc_client_node))
        logger.info(dfu_common.get_chip_arch_type_support(self.rpc_client_node))
        logger.info(dfu_common.get_chip_arch_type_support(self.rpc_client_node))
        
        params = {}
        params["driver_name"] = dev_path
        params["protocol_type"] = protocol_type
        params["chip_arch_type"] = arch_type
        params["chip_type"] = chip_type

        response = self.rpc_client_node.call("DfuProgInstanceCreate",**params)
        logger.info(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)
        
        
        