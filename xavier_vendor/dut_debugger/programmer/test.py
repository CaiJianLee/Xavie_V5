#-*- coding: UTF-8 -*-
import sys
import os
import re
import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger
from programmer.dfucommon import dfu_common
from programmer.chipprog.cortexmprog import CortexMProg
from programmer.chipprog.psoc4prog import Psoc4Prog
from programmer.dfuapp.dfu_app import Programmer
import time

def test():

    #create rpc client
    dfu_rpc_node = Xavier.XavierRpcClient("127.0.0.1",3456,"tcp")
    #create prog instance
    # thearray = [1,2,3,4,5,6]
    # params = {}
    # params["name"] = "hehesimida"
    # params["array"] = thearray
    # ret = dfu_rpc_node.call("sayHello",**params)
    # print(ret["return"])
    prog_instance = Psoc4Prog(dfu_rpc_node)
    print("----------------1-----------------")
    print(prog_instance.create_instance("/dev/AXI4_SWD_Core_0","cy8c4248"))
    
    print("----------------2-----------------")
    print(prog_instance.instance_initial(2500000))
    print("----------------3-----------------")
    print(prog_instance.dut_initial())
    print("----------------4-----------------")
    print(prog_instance.dut_storage_erase_all())
    print("----------------5-----------------")
    print(prog_instance.dut_storage_infusing("/opt/seeing/tftpboot/BlinkingLED.bin",0x0000000,0x000000,32*1024))
    print("----------------6-----------------")
    print(prog_instance.dut_storage_checkout("/opt/seeing/tftpboot/BlinkingLED.bin",0x0000000,0x000000,32*1024))
    print("----------------7-----------------")
    print(prog_instance.dut_exit())
    print("----------------8-----------------")
    print(prog_instance.destroy_instance())
    print("----------------9-----------------")

    pass


def test2():
    dfu_rpc_node = Xavier.XavierRpcClient("127.0.0.1",3456,"tcp")
    prog_instance = Programmer(dfu_rpc_node)
    print("----------------1-----------------")
    # ret = prog_instance.create_target("/dev/AXI4_SWD_Core_0","cy8c4248",2500000)
    # ret = prog_instance.create_target("/dev/AXI4_SPI_Prog_Core_0","w25q128",2500000)
    #ret = prog_instance.create_target("/dev/AXI4_SWD_Core_0","nrf52xxx",500000)
    ret = prog_instance.create_target("/dev/AXI4_SWD_Core_0","stm32l4xx",500000)
    print(ret[1])
    # ret = prog_instance.target_initial()
    ret = prog_instance.target_erase_all()
    # ret = prog_instance.target_programming("/root/BlinkingLED.bin",32*1024)
    print(ret[1])
    firmware_size = os.path.getsize("/root/STM32L476RG_NUCLEO.bin")
    print("firmware_size = %d"%(os.path.getsize("/root/STM32L476RG_NUCLEO.bin")))
    ret = prog_instance.target_programming_only("/root/STM32L476RG_NUCLEO.bin",firmware_size)
    ret = prog_instance.target_checkout("/root/STM32L476RG_NUCLEO.bin",firmware_size)
    ret = prog_instance.target_programming("/root/STM32L476RG_NUCLEO.bin",firmware_size)
    # print("----------------3-----------------")
    print(ret[1])
    # print("----------------4-----------------")
    ret = prog_instance.destroy_target()
    print(ret[1])
    # print("----------------5-----------------")
    pass



if __name__ == "__main__":
#     test()
    test2()
    pass













