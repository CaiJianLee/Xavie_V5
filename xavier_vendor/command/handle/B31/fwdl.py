import command.server.handle_utility as utility
from collections import OrderedDict
from ee.common import xavier as Xavier
import re
import time
import os
import json
from ee.common import logger
import subprocess
from ee.board.programmer.dfuapp.dfu_app import ProgApp
import ee.common.utility as CommonUtility 
from ee.ipcore.axi4_gpio import Axi4Gpio

"cortexm0"
"cortexm3"
"cortexm4"
"cortexm7"
"stm32l4xx"
"stm32l0xx"
"stm32F3xx"
"stm32F4xx"
"stm32F7xx"
"cy8c4248"
"cpyd1xxx"
"cpyd2xxx"
"cy8c4248l"
"nrf51xxx"
"nrf52xxx"
"w25q128"
"at25s128"
"w25x"
"s25l"
"w25q256"

global _g_fwdl_current_frequency_hz
global _g_fwdl_config_list

_g_fwdl_current_frequency_hz = None
_g_fwdl_config_list = None
fwdl_configure_path = "/opt/seeing/app/fwdl_config/Fwdl_Profile.json"
if os.path.exists(fwdl_configure_path):
    _g_fwdl_config_list = CommonUtility.load_json_file(fwdl_configure_path)
else:
    _g_fwdl_config_list = None
    print("_g_fwdl_config_list is None!")
    
def get_firmware_path(channel):
    #
    global _g_fwdl_config_list
    if _g_fwdl_config_list != None:
        path = _g_fwdl_config_list["support_channel"][channel]["firmware_path"]
        cmd = "mkdir -p %s"%path
        os.system(cmd)
        return _g_fwdl_config_list["support_channel"][channel]["firmware_path"]
    return False

def get_dev_path(channel,chip_type):
    global _g_fwdl_config_list
    logger.warning(chip_type)
    protocol_name = None
    if _g_fwdl_config_list != None:
        for key in _g_fwdl_config_list["protocol_chip_support"].keys():
            for item in _g_fwdl_config_list["protocol_chip_support"][key]:
                if chip_type == item:
                    protocol_name = key
                    logger.warning(protocol_name)
                    break
                    
            if protocol_name == key:
                break
        if protocol_name == None:
            return False
        dev_path = _g_fwdl_config_list["support_channel"][channel]["protocol_driver_config"][protocol_name]
        spi_switch = _g_fwdl_config_list["support_channel"][channel]["protocol_driver_config"]["spi_switch"]
        if spi_switch != "none":
            gpio_dev = Axi4Gpio("/dev/AXI4_GPIO_0")
            gpio_dev.gpio_set(eval(spi_switch))

        logger.warning(protocol_name)
        logger.warning(dev_path)
        if os.path.exists(dev_path):
            logger.warning(dev_path)
            return dev_path
        else:
            return False
    return False

def get_frequency_config(process_name,chip_type):
    #process_name = "read_id","erase_chip","program_only","verify","program"
    global _g_fwdl_config_list
    global _g_fwdl_current_frequency_hz
    
    read_frequency = None
    if _g_fwdl_config_list != None:
        frequency_group = _g_fwdl_config_list["chip_process_configure"][process_name]["frequency_hz"]
        for freq_hz in frequency_group.keys():
            for item in frequency_group[freq_hz]:
                if item == chip_type:
                    read_frequency = int(freq_hz,10)
                    break
            if read_frequency != None:
                break
        if read_frequency == None:
            return _g_fwdl_config_list["chip_process_configure"][process_name]["default_frequency_hz"]
        return read_frequency
    return False

def get_prog_rpc_node(channel):
    global _g_fwdl_config_list
    prog_rpc_node = False
    if _g_fwdl_config_list != None:
        server_ip = _g_fwdl_config_list["support_channel"][channel]["rpc_server_config"]["ip"]
        server_port = _g_fwdl_config_list["support_channel"][channel]["rpc_server_config"]["port"]
        prog_rpc_node = Xavier.XavierRpcClient(server_ip,server_port,"tcp")
        logger.warning(server_ip)
        logger.warning(str(server_port))
        return prog_rpc_node
    return False


#----------------executing process--------------------------
def fwdl_executing_process(channel,process_name,chip_type,executing_config_list = None):
    "executing_config_list = \
        [\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        ........]"
    global _g_fwdl_config_list
    global _g_fwdl_current_frequency_hz
    
    ret_str = ""
    frequency_hz = None
    #get channel dev path
    dev_path = get_dev_path(channel,chip_type)
    if dev_path == False:
        return False,"channel dev path is not exist!"
    #get frequency
    if _g_fwdl_current_frequency_hz != None:
        frequency_hz = _g_fwdl_current_frequency_hz
    else:
        frequency_hz = get_frequency_config(process_name,chip_type)
        if frequency_hz == False:
            return False,"frequency is not configure !"
    logger.warning(str(frequency_hz))
    #get prog rpc node
    prog_rpc_node = get_prog_rpc_node(channel)
    if prog_rpc_node == False:
        return False,"rpc server is not exist !"
    #get dfu instance
    prog_instance = ProgApp(prog_rpc_node)
    #create target
    prog_state,prog_str = prog_instance.create_target(dev_path,chip_type,frequency_hz)
    ret_str += prog_str
    if prog_state == False:
        return False,ret_str
    #executing processs
    if process_name == "read_id":#read identify code
        prog_state,prog_str = prog_instance.target_initial()#initial target
        ret_str += prog_str
        if prog_state == False:
            return False,ret_str
        #destroy instance

        prog_state,prog_str = prog_instance.destroy_target()
        ret_str += prog_str
        if prog_state == False:
            return False,ret_str
        pass
    elif process_name == "erase_chip":#erase all
        if executing_config_list != None:
            for item in executing_config_list:
                target_addr = int(item["target_addr"],16)
                size = int(item["size"],10)
            prog_state,prog_str = prog_instance.target_erase(target_addr,size)
        else:
            prog_state,prog_str = prog_instance.target_erase()#erase all
        ret_str += prog_str
        if prog_state == False:
            return False,ret_str
         #destroy instance
        prog_state,prog_str = prog_instance.destroy_target()
        ret_str += prog_str
        if prog_state == False:
            return False,ret_str
        pass
    elif (process_name == "program_only") or (process_name == "verify") or (process_name == "program") or ((process_name == "readverify")):#not erase program   
        target_size = 0
        for item in executing_config_list:
            firmware_path = get_firmware_path(channel)+'/'+item["target_file"]
            target_addr = None
            if "target_addr" not in item.keys():
                target_addr_group = _g_fwdl_config_list["chip_process_configure"]["program_only"]['default_addr']
                for addr_key in target_addr_group.keys():
                    for item_chip in target_addr_group[addr_key]:
                        if item_chip == chip_type:
                            target_addr = int(addr_key,16)
                            break
                if target_addr == None:
                    ret_str += "do not have target address"
                    #destroy instance
                    prog_state,prog_str = prog_instance.destroy_target()
                    ret_str += prog_str
                    if prog_state == False:
                        return False,ret_str
                    return prog_state,ret_str
            else:
                target_addr = int(item["target_addr"],16)
            
            if process_name == "program_only" :
                #programming
                prog_state,prog_str = prog_instance.target_programming_only(\
                                                                    firmware_path,item["size"],target_addr,item["file_offset"])
                ret_str += prog_str
                if prog_state == False:
                    return False,ret_str
            elif process_name == "program":
                #programming only
                prog_state,prog_str = prog_instance.target_programming(\
                                                                    firmware_path,item["size"],target_addr,item["file_offset"])
                ret_str += prog_str
                if prog_state == False:
                    return False,ret_str
            elif process_name == "verify":
                #verify
                prog_state,prog_str = prog_instance.target_checkout(\
                                                                    firmware_path,item["size"],target_addr,item["file_offset"])
                ret_str += prog_str
                if prog_state == False:
                    return False,ret_str
            elif process_name == "readverify":
                #readverify to read the target log
                # firmware_path+=".readback"
                os.system("touch %s"%firmware_path)
                prog_state,prog_str = prog_instance.read_target_storage(\
                                                                    firmware_path,item["size"],target_addr)
                ret_str += prog_str
                if prog_state == False:
                    return False,ret_str
        #destroy instance
        prog_state,prog_str = prog_instance.destroy_target()
        ret_str += prog_str
        if prog_state == False:
            return False,ret_str
        pass
    else:
        ret_str += "do not have the operation !"
        return False,ret_str
    
    #destroy instance
    prog_state,prog_str = prog_instance.destroy_target()
    ret_str += prog_str
    if prog_state == False:
        return False,ret_str
    return True,ret_str
#---------------------------------------------------------handle---------------------------------------------
    
def programmer_id_handle(params):
    help_info = "programmer id(<channel>,<chip type>)$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n\
\tchip type:"+ str(json.dumps(_g_fwdl_config_list["support_chip"])).replace('"','')+";\r\n"

    '''  init information '''
    base_param_index = 0
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if param_count != 3 and param_count != 2 :
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
    
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            channel_str = params[index]
        if index == base_param_index+1:
            chip_type = params[base_param_index+1]

               
    #-------------------doing------------------
    ret_str = ""
    prog_state,prog_str = fwdl_executing_process(channel_str,"read_id",chip_type)
    ret_str += prog_str
    if prog_state == False:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],ret_str)
    
    return utility.handle_done(ret_str)#fwdl_executing_str idcode
    
def programmer_handle(params):
    help_info = "programmer(<channel>,<chip type>,<firmware path>,{<target_address>})$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n\
\tchip type:"+ str(json.dumps(_g_fwdl_config_list["support_chip"])).replace('"','')+"$\r\n\
\tfirmware path:the firmware want to be download$\r\n\
\ttarget_address:target_address;\r\n"

    '''  init information '''

    base_param_index = 0
    target_address = None
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if param_count < 3 :
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
    
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            channel_str = params[index]
        if index == base_param_index+1:
            chip_type = params[base_param_index+1]
        if index == base_param_index+2:
            fwdl_firmware_file = params[base_param_index+2]
        if index == base_param_index+3:
            target_address = params[base_param_index+3]
            
    #-------------------doing------------------
    ret_str = ""
    if os.path.exists(get_firmware_path(channel_str)+'/'+fwdl_firmware_file):
        file_size = os.path.getsize(get_firmware_path(channel_str)+'/'+fwdl_firmware_file)
    else:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"target firmware file is not exist !")
    "executing_config_list = \
        [\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        ........]"
    executing_config_list = []
    executing_config_dict = {}
    if target_address != None:
        executing_config_dict["target_addr"] = target_address
    executing_config_dict["target_file"] = fwdl_firmware_file
    executing_config_dict["file_offset"] = 0
    executing_config_dict["size"] = file_size
    
    executing_config_list.append(executing_config_dict)
    prog_state,prog_str = fwdl_executing_process(channel_str,"program",chip_type,executing_config_list)
    ret_str += prog_str
    if prog_state == False:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],ret_str)
    
    return utility.handle_done(ret_str)#fwdl_executing_str idcode
    
def programmer_checkout_handle(params):
    help_info = "programmer checkout(<channel>,<chip type>,<firmware path>,{<target_address>})$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n\
\tchip type:"+ str(json.dumps(_g_fwdl_config_list["support_chip"])).replace('"','')+"$\r\n\
\tfirmware path:the firmware want to be checkout$\r\n\
\ttarget_address:target_address;\r\n"

    '''  init information '''
    base_param_index = 0
    target_address = None
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if param_count < 3 :
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
    
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            channel_str = params[index]
        if index == base_param_index+1:
            chip_type = params[base_param_index+1]
        if index == base_param_index+2:
            fwdl_firmware_file = params[base_param_index+2]
        if index == base_param_index+3:
            target_address = params[base_param_index+3]
            
    #-------------------doing------------------
    ret_str = ""
    if os.path.exists(get_firmware_path(channel_str)+'/'+fwdl_firmware_file):
        file_size = os.path.getsize(get_firmware_path(channel_str)+'/'+fwdl_firmware_file)
    else:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"target firmware file is not exist !")
    "executing_config_list = \
        [\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        ........]"
    executing_config_list = []
    executing_config_dict = {}
    if target_address != None:
        executing_config_dict["target_addr"] = target_address
    executing_config_dict["target_file"] = fwdl_firmware_file
    executing_config_dict["file_offset"] = 0
    executing_config_dict["size"] = file_size
    
    executing_config_list.append(executing_config_dict)
    prog_state,prog_str = fwdl_executing_process(channel_str,"verify",chip_type,executing_config_list)
    ret_str += prog_str
    if prog_state == False:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],ret_str)
    
    return utility.handle_done(ret_str)#fwdl_executing_str idcode

def programmer_only_handle(params):
    help_info = "programmer only(<channel>,<chip type>,<firmware path>,{<target_address>})$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n\
\tchip type:"+ str(json.dumps(_g_fwdl_config_list["support_chip"])).replace('"','')+"$\r\n\
\tfirmware path:the firmware want to be download$\r\n\
\ttarget_address:target_address;\r\n"

    '''  init information '''
    base_param_index = 0
    target_address = None
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if param_count < 3 :
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
    
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            channel_str = params[index]
        if index == base_param_index+1:
            chip_type = params[base_param_index+1]
        if index == base_param_index+2:
            fwdl_firmware_file = params[base_param_index+2]
        if index == base_param_index+3:
            target_address = params[base_param_index+3]
            
    #-------------------doing------------------
    ret_str = ""
    if os.path.exists(get_firmware_path(channel_str)+'/'+fwdl_firmware_file):
        file_size = os.path.getsize(get_firmware_path(channel_str)+'/'+fwdl_firmware_file)
    else:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"target firmware file is not exist !")
    "executing_config_list = \
        [\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        ........]"
    executing_config_list = []
    executing_config_dict = {}
    if target_address != None:
        executing_config_dict["target_addr"] = target_address
    executing_config_dict["target_file"] = fwdl_firmware_file
    executing_config_dict["file_offset"] = 0
    executing_config_dict["size"] = file_size
    
    executing_config_list.append(executing_config_dict)
    prog_state,prog_str = fwdl_executing_process(channel_str,"program_only",chip_type,executing_config_list)
    ret_str += prog_str
    if prog_state == False:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],ret_str)
    
    return utility.handle_done(ret_str)#fwdl_executing_str idcode

def programmer_readverify_handle(params):
    help_info = "programmer readverify(<channel>,<chip type>,<firmware path>,<target_address>,<size>)$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n\
\tchip type:"+ str(json.dumps(_g_fwdl_config_list["support_chip"])).replace('"','')+"$\r\n\
\tfirmware path:the firmware want to be readback$\r\n\
\ttarget_address:target_address(hex),eg:0x00$\r\n\
\tsize:size of read (hex),eg:0x100000;\r\n"

    '''  init information '''
    base_param_index = 0
    target_address = None
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if param_count < 3 :
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
    
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            channel_str = params[index]
        if index == base_param_index+1:
            chip_type = params[base_param_index+1]
        if index == base_param_index+2:
            fwdl_firmware_file = params[base_param_index+2]
        if index == base_param_index+3:
            target_address = params[base_param_index+3]
        if index == base_param_index+4:
            target_size = params[base_param_index+4]
    #-------------------doing------------------
    ret_str = ""
    fwdl_firmware_file +=".readback"
    # if os.path.exists(get_firmware_path(channel_str)+'/'+fwdl_firmware_file):
    #     file_size = os.path.getsize(get_firmware_path(channel_str)+'/'+fwdl_firmware_file)
    # else:
    #     return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"target firmware file is not exist !")
    "executing_config_list = \
        [\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        {'target_addr':offset_val,'target_file':file_name,'file_offset':offset_val,'size':size_to_program_or_verify},\
        ........]"
    executing_config_list = []
    executing_config_dict = {}
    if target_address != None:
        executing_config_dict["target_addr"] = target_address
    executing_config_dict["target_file"] = fwdl_firmware_file
    # executing_config_dict["file_offset"] = 0
    executing_config_dict["size"] = int(target_size,16)
    
    executing_config_list.append(executing_config_dict)
    prog_state,prog_str = fwdl_executing_process(channel_str,"readverify",chip_type,executing_config_list)
    ret_str += prog_str
    if prog_state == False:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],ret_str)
    return utility.handle_done(ret_str)#fwdl_executing_str idcode


def programmer_erase_handle(params):
    help_info = "programmer erase(<channel>,<chip type>,{<target_address>,<size>})$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n\
\tchip type:"+ str(json.dumps(_g_fwdl_config_list["support_chip"])).replace('"','')+"$\r\n\
\ttarget_address:target_address;\r\n\
\tsize:erase size;\r\n"

    '''  init information '''
    base_param_index = 0
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    '''  params analysis '''
    param_count = len(params)
    if param_count != 2 and param_count != 4 :
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
    target_address = None
    erasesize = None
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            channel_str = params[index]
        if index == base_param_index+1:
            chip_type = params[base_param_index+1]
        if index == base_param_index+2:
            target_address = params[base_param_index+2]
        if index == base_param_index+3:
            erasesize = params[base_param_index+3]
               
    executing_config_list = []
    executing_config_dict = {}
    if target_address != None and erasesize != None:
        executing_config_dict["target_addr"] = target_address
        executing_config_dict["size"] = erasesize
    
    executing_config_list.append(executing_config_dict)
    #-------------------doing------------------
    ret_str = ""
    if target_address != None and erasesize != None:
        prog_state,prog_str = fwdl_executing_process(channel_str,"erase_chip",chip_type,executing_config_list)
    else:
        prog_state,prog_str = fwdl_executing_process(channel_str,"erase_chip",chip_type)
    ret_str += prog_str
    if prog_state == False:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],ret_str)
    
    return utility.handle_done(ret_str)#fwdl_executing_str idcode
    
def programmer_firmware_check_handle(params):
    help_info = "firmware check(<channel>)$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n"

    '''  init information '''
    firmware_file = ""
    firmware_group = []
    base_param_index = 0
    
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
        pass

    param_count = len(params)
    if param_count > 1:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
    
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            regular_expression = re.match( r'ch(\w+)', params[index])
            if regular_expression is None:
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
            channel = int(regular_expression.group(1), 10) - 1
            if(channel>3 or channel <0):
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
            
    channel_path = fwdl_firmware_path+"/ch"+str(channel+1)        
#     logger.info(channel_path)

    if (os.path.isdir(channel_path)) == False:
        os.mkdir(channel_path)
        
    firmware_group = os.listdir(channel_path)
    
    firmware_file = ""
    for file_name in firmware_group:
        file_size = os.path.getsize(channel_path+"/"+file_name)
        file_time_stamp = os.stat(channel_path+"/"+file_name)
        file_time = time.localtime(file_time_stamp.st_ctime)
        file_time_str = str(file_time[0])+"-"+str(file_time[1])+"-"+str(file_time[2])+" "+str(file_time[3])+':'+str(file_time[4])+':'+str(file_time[5])
        
        check_md5_cmd = "md5sum "+channel_path+"/"+file_name+" |awk '{print $1}'  > "+channel_path+"/"+file_name+".md5val"
        os.system(check_md5_cmd)
        
        with open(channel_path+"/"+file_name+".md5val")  as md5file:
            md5val = md5file.read()
        
        md5file.close()
        os.system("rm "+channel_path+"/"+file_name+".md5val")
        
#         logger.info(file_time_str)
        firmware_file += file_name+"  "+str(file_size)+"  "+file_time_str+" "+md5val+"\r\n"

    if firmware_file != "":
        firmware_file = firmware_file[0:-1]
    
    return utility.handle_done(firmware_file)

def programmer_firmware_erase_handle(params):
    help_info = "firmware erase(<channel>)$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n"
    
    '''  init information '''
    firmware_file = ""
    firmware_group = []
    base_param_index = 0
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    param_count = len(params)
    if param_count > 1:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
    
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            regular_expression = re.match( r'ch(\w+)', params[index])
            if regular_expression is None:
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
            channel = int(regular_expression.group(1), 10) - 1
            if(channel>3 or channel <0):
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
            
    channel_path = fwdl_firmware_path+"/ch"+str(channel+1) 
    if (os.path.isdir(channel_path)) == False:
        os.mkdir(channel_path)
        
    os.system("rm "+channel_path+"/*")
    
    return utility.handle_done()
    
def programmer_abort_handle(params):
    help_info = "programmer abort(<channel>)$\r\n\
\tchannel:"+str(json.dumps(list(_g_fwdl_config_list['support_channel'].keys()))).replace('"','') +"$\r\n"
    base_param_index = 0
    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    param_count = len(params)
    if param_count > 1:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'].value,"param length error")
     
    for index in range(base_param_index, param_count):
        if index == base_param_index:
            regular_expression = re.match( r'ch(\w+)', params[index])
            if regular_expression is None:
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
            channel = int(regular_expression.group(1), 10) - 1
            if(channel>3 or channel <0):
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
    
    abord_process_cmd = fwdl_executing_main_file+str(channel+1)
    
    os.system("killall -9 "+abord_process_cmd)

    return utility.handle_done()


