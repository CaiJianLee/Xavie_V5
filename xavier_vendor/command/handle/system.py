#-*- coding: UTF-8 -*-
from __future__ import division
import os
import re
import json
import time
import os.path
import sys
import zmq
import command.server.handle_utility as utility
import ee.common.utility as ee_utility
from ee.common import net
from ee.common import logger
from ee.ipcore.axi4_sysreg import Axi4Sysreg

version_path="/opt/seeing/version.txt"
update_file_path="/opt/seeing/tftpboot/"
update_file_string="ARM_Board_D3"

''' version information'''
version_info = {
        1:{"name":"Name",          "msg":"ARM Board D3-IA863",   "full_name":"MCU Software name"},
        2:{"name":"SW",              "msg":"4.00.02",                           "full_name":",MCU Software version"},
        3:{"name":"HW Name",    "msg":"ARM Board D3",                "full_name":",Hardware name"},
        4:{"name":"HW",             "msg":"D3.0",                                 "full_name":",Hardware version"},
        5:{"name":"Compile time","msg":"Dec 21 2016 19:04:22",    "full_name":",Compile time"},
        6:{"name":"FB",                "msg":"0.0",                                  "full_name":",FPGA Bom"},
        7:{"name":"FW",               "msg":"0.0",                                  "full_name":",FPGA version"},
        8:{"name":"Author",         "msg":"SmartGiant",           "full_name":",Author"},
    }

def get_fpga_version():
    system_page_name = '/dev/AXI4_SYSREG'
    version_device = Axi4Sysreg(system_page_name)
    fpga_version = version_device.version_get()
    if (True == isinstance(fpga_version, str)):
        version_info[7]["msg"] = 'V' + fpga_version
    else:
        version_info[7]["msg"] = 'V00.00'

def get_seeing_version():
    file_object = open(version_path)
    version_str = ''
    project_str = 'ARM Board D3-'
    compile_str = ''
    for line in file_object:
        version_object = re.match(r'seeing=(\w+).(\w+).(\w+)',line)
        project_object = re.match(r'project=(\w+)',line)
        if version_object is not None:
            version_str = version_object.group(1)
            version_str += "."
            version_str += version_object.group(2)
            version_str += "."
            version_str+= version_object.group(3)
        if project_object is not None :
            project_str += project_object.group(1)
        compile_object = re.match(r'compile_time=(\w+)-(\w+)-(\w+)--(\w+):(\w+):(\w+)',line)
        if compile_object is not None :
            compile_str += compile_object.group(1)
            compile_str += '-'
            compile_str += compile_object.group(2)
            compile_str += '-'
            compile_str += compile_object.group(3)
            compile_str += ' '
            compile_str += compile_object.group(4)
            compile_str += ':'
            compile_str += compile_object.group(5)
            compile_str += ':'
            compile_str += compile_object.group(6)

    file_object.close()
    return (project_str,version_str,compile_str)

#get_seeing_version()
(version_info[1]["msg"],version_info[2]["msg"],version_info[5]["msg"]) = get_seeing_version()
#version_info[2]["msg"] = "4.00.02"

@utility.timeout(1)
def help_handle(params):
    buf = "$\r\n--------------------    --------------------$\r\n"
    try:
        if True == os.path.exists(os.path.dirname(sys.argv[0]) + "/handles_config.json"):
            json_file = '%s/handles_config.json'%(os.path.dirname(sys.argv[0]))
        else:
            json_file = '%s/command/handle/handles_config.json'%(os.environ.get("PYTHON_HOME", "/opt/seeing/app"))
        handles_file = open(json_file)
    except Exception as e:
        logger.error("open handles config file errer !!!")
        return
    for each_line in handles_file :
        line = each_line.strip()
        line = line.strip(',')
        msg = None
        try:
            msg = json.loads(line)
        except Exception as e:
            continue
        buf += msg["cmd"]
        #目的对其
        cmd_len = len(msg["cmd"])
        count_t = 3 - int(cmd_len/8)
        for index in range(0,count_t):
            buf +="\t"

        buf += msg["description"]
        buf += "$\r\n"
    buf += "--------------------    --------------------$\r\n"
    handles_file .close()
    return buf

def __net_information_handle(module, net_information):
    network_information = net.read_network_information()

    if module != 'net':
        '''
        if "user" != network_information["mode"]:
            return True
        '''

        if module == 'mac':
            return net.set_network_information("user:mac", net_information)

        if module == 'ip':
            return net.set_network_information("user:ip", net_information)

        if module == 'gate':
            return net.set_network_information("user:gateway", net_information)

        if module == 'mask':
            return net.set_network_information("user:mask", net_information)
    else:
        if net_information == 'default':
            return net.set_network_information("mode", "default")

        elif net_information == 'user':
            return net.set_network_information("mode", "user")

        else:
             return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")

@utility.timeout(1)
def net_set_handle(params):

    help_info = "net set({<module>,<content>})$\r\n\
\tmodule= (mac,ip,mask,gate,net) $\r\n\
\tmodule=mac$\r\n\
\tcontent=(format=Address1:Address2...:Address6)$\r\n\
\taddressx:(00-FF) Hex$\r\n\
\tmodule=ip$\r\n\
\tcontent=(format=Address1.Address2.Address3.Address4)$\r\n\
\tAddressx:(0-255) $\r\n\
\tmodule=mask$\r\n\
\tcontent=(format=Address1.Address2.Address3.Address4)$\r\n\
\tAddressx:(0-255) $\r\n\
\tmodule=gate\r\n\
\tcontent=(format=Address1.Address2.Address3.Address4)$\r\n\
\tAddressx:(0-255) $\r\n\
\tmodule=net$\r\n\
\tcontent= (default,user)\r\n" 

    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)

    ''' parametr analysis '''
    if len(params) != 2:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param  length error")  

    if params[0] == 'mac':

        regular_expression = re.match( r'(\w+)\:(\w+)\:(\w+)\:(\w+)\:(\w+)\:(\w+)', params[1])

        if regular_expression is None:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"regular expression error")

        if False == __net_information_handle(params[0], params[1]):
            return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"message execute failed")

    elif params[0] == 'ip':
        ip = ['','','','']

        regular_expression = re.match( r'(\w+)\.(\w+)\.(\w+)\.(\w+)', params[1])

        if regular_expression is None:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"regular expression error")

        if False == __net_information_handle(params[0], params[1]):
            return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"message execute failed")

    elif params[0] == 'mask':
        mask = ['','','','']

        regular_expression = re.match( r'(\w+)\.(\w+)\.(\w+)\.(\w+)', params[1])

        if regular_expression is None:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"regular expression error")

        if False == __net_information_handle(params[0], params[1]):
            return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"message execute failed")

    elif params[0] == 'gate':
        gate = ['','','','']

        regular_expression = re.match( r'(\w+)\.(\w+)\.(\w+)\.(\w+)', params[1])

        if regular_expression is None:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"regular expression error")

        if False == __net_information_handle(params[0], params[1]):
            return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"message execute failed")

    elif params[0] == 'net':
        result = __net_information_handle(params[0], params[1])
        if False == result:
            return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"message execute failed")
        elif True == result:
            return utility.handle_done()
        elif result:
            return result

    else:
         return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param  error") 
    return utility.handle_done()
#end of net set handle

#begin of net read handle
@utility.timeout(1)
def net_read_handle(params):

    help_info = "net read({<module>})$\r\n\
\tmodule= (mac,ip,mask,gate,net,user) $\r\n"

    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)

    ''' parametr analysis '''
    if len(params) != 1:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param  length error")

    network_information = net.read_network_information()

    output_str = ''
    mode = network_information["mode"]
    if params[0] == 'mac':
        output_str = output_str + 'mac: ' + '%s'%(network_information[mode]["mac"])
    elif params[0] == 'ip':
        output_str = output_str + 'ip: ' + '%s'%(network_information[mode]["ip"])
    elif params[0] == 'gate':
        output_str = output_str + 'gate: ' + '%s'%(network_information[mode]["gateway"])
    elif params[0] == 'mask':
        output_str = output_str + 'mask: ' + '%s'%(network_information[mode]["mask"])
    elif params[0] == 'net':
        output_str = output_str + '%s,'%(mode)
        output_str = output_str +  'mac: ' + '%s,'%(network_information[mode]["mac"])
        output_str = output_str + 'ip: ' + '%s,'%(network_information[mode]["ip"])
        output_str = output_str + 'gate: ' + '%s,'%(network_information[mode]["gateway"])
        output_str = output_str + 'mask: ' + '%s'%(network_information[mode]["mask"])
    elif params[0] == 'user':
        mode = 'user'
        output_str = output_str + '%s,'%(mode)
        output_str = output_str +  'mac: ' + '%s,'%(network_information[mode]["mac"])
        output_str = output_str + 'ip: ' + '%s,'%(network_information[mode]["ip"])
        output_str = output_str + 'gate: ' + '%s,'%(network_information[mode]["gateway"])
        output_str = output_str + 'mask: ' + '%s'%(network_information[mode]["mask"])
    else:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param  error") 

    return utility.handle_done(output_str) 
#end of net read handle

@utility.timeout(1)
def version_handle(params):
    help_info = "version(<number>)$\r\n\
\tnumber=(0-255) $\r\n\
\t    1=MCU $\r\n\
\t    2=SoftName $\r\n\
\t    3=Hardware $\r\n\
\t    4=FPGA $\r\n\
\t    5=FPGA BOM $\r\n\
\t    6=MCU FPGA Hardware $\r\n\
\t    254=MCU Compile $\r\n\
\t    other=all information $"
        
            #help
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
        #parametr analysis
    param_count = len(params)
    if param_count != 1 :
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'] - 1,"param error")
    
    #result
    version_num = int(params[0])
    msg=""
    if version_num == 1: #SW
        msg += version_info[2]["name"]
        msg += "="
        msg += version_info[2]["msg"]
    elif version_num == 2:#name
        msg += version_info[1]["name"]
        msg += "="
        msg += version_info[1]["msg"]
    elif version_num == 3:#HN && HW
        msg += version_info[3]["name"]
        msg += "="
        msg += version_info[3]["msg"]
        msg += ","
        msg += version_info[4]["name"]
        msg += "="
        msg += version_info[4]["msg"]
    elif version_num == 4:  #FW
        msg += version_info[7]["name"]
        msg += "="
        msg += version_info[7]["msg"]
    elif version_num == 5:# FB
        msg += version_info[6]["name"]
        msg += "="
        msg += version_info[6]["msg"]
    elif version_num == 6:# name &&SW && FW
        msg += version_info[1]["name"]
        msg += "="
        msg += version_info[1]["msg"]
        msg += ","
        msg += version_info[2]["name"]
        msg += "="
        msg += version_info[2]["msg"]
        msg += ","
        msg += version_info[7]["name"]
        msg += "="
        msg += version_info[7]["msg"]
    elif version_num == 254:
        msg += version_info[5]["name"]
        msg += "="
        msg += version_info[5]["msg"]
    else :
        msg += "$\r\n"
        for index in version_info:
            msg +=version_info[index]["full_name"]
            msg += ":"
            msg += version_info[index]["msg"]
            msg += "$\r\n"
    return utility.handle_done(msg)

def _check_log_name(name):
    _config = ee_utility.load_json_file(ee_utility.get_app_path()+"/monitor/monitor.json")
    for key in _config:
        if ";;log_config" == key:
            if name in _config[key] and _config[key][name].has_key("port"):
                return True
            else:
                return False
    return False

@utility.timeout(1)
def logupload_open_handle(params):
    help_info = "logupload open({<name>})$\r\n\
\tname: log's name $\r\n"

    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)

    ''' parametr analysis '''
    params_count = len(params)
    if not params_count == 1:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    name = params[0]
    if False == isinstance(name, str):
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")

    if False == _check_log_name(name):
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"%s did not register information for upload"%(name))

    context = zmq.Context()

    # Socket to talk to clients
    publisher = context.socket(zmq.PUB)
    # bind port
    try:
        publisher.bind('tcp://*:22730')
        msg = json.dumps({b'%s'%((name.split(".log")[0]).upper()):{b"upload":True}})
        for i in range(0, 3):
            publisher.send(msg)
            time.sleep(0.1)
    except Exception:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"open log upload error[socket invalid]")

    logger.info("logupload_open_handle success")
    return utility.handle_done()

@utility.timeout(1)
def logupload_close_handle(params):
    help_info = "logupload close({<name>})$\r\n\
\tname: log's name $\r\n"

    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)

    ''' parametr analysis '''
    params_count = len(params)
    if not params_count == 1:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    name = params[0]
    if False == isinstance(name, str):
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")

    if False == _check_log_name(name):
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"%s did not register information for upload"%(name))

    context = zmq.Context()

    # Socket to talk to clients
    publisher = context.socket(zmq.PUB)
    # bind port
    try:
        publisher.bind('tcp://*:22730')
        msg = json.dumps({b'%s'%((name.split(".log")[0]).upper()):{b"upload":False}})
        for i in range(0, 3):
            publisher.send(msg)
            time.sleep(0.1)
    except Exception:
        return utility.handle_error(utility.handle_errorno['handle_errno_execute_failure'],"open log upload error[socket invalid]")

    logger.info("logupload_close_handle success")
    return utility.handle_done()

@utility.timeout(1)
def log_level_handle(params):
    help_info = "set log level({<name>},{<locallevel>,<uploadlevel>})$\r\n\
\tname: log's name $\r\n \
\tlocallevel=(debug,info,warning,error,critical)$\r\n \
\tuploadlevel=(debug,info,warning,error,critical)\r\n"

    levels = ["info", "debug", "warning", "error", "critical"]

    ''' help '''
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)

    ''' parametr analysis '''
    params_count = len(params)
    if not 3 == params_count:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    name = ""
    locallevel = ""
    uploadlevel = ""
    for index in range(0,params_count):
        if index == 0:
            name = params[index]
        elif index == 1:
            locallevel = params[index]
        elif index == 2:
            uploadlevel = params[index]
        else:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    if not name:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"log's name must is not null")

    if locallevel not in levels:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'], \
                                    "locallevel must is one of (debug,info,warning,error,critical)")

    if uploadlevel and uploadlevel not in levels:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'], \
                                    "uploadlevel must is one of (debug,info,warning,error,critical)")

    context = zmq.Context()

    # Socket to talk to clients
    publisher = context.socket(zmq.PUB)
    # bind port
    publisher.bind('tcp://*:22730')
    msg = json.dumps({b'%s'%((name.split(".log")[0]).upper()):{b"locallevel":b"%s"%(locallevel.upper()), b"uploadlevel":b"%s"%(uploadlevel.upper())}})
    for i in range(0, 3):
        publisher.send(msg)
        time.sleep(0.1)

    logger.info("log_level_handle success")
    return utility.handle_done()

@utility.timeout(1)
def synctime_handle(params):
    help_info = "synctime({<-option>},{<second>,<milisecond>})$\r\n\
\toption: (r(read),w(write)),default:r $\r\n \
\tsecond:(>0),option=w$\r\n \
\tmillisecond:(0-1000),option=w\r\n"

    ''' default information '''
    option = 'r'

    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)

    ''' parametr analysis '''
    params_count = len(params)
    if params_count > 3:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")  

    for index in range(0,params_count):
        if index == 0:
            temp_value = params[index]
            if temp_value[0] == '-' and len(temp_value) == 2:
                option = temp_value[1]
            else:
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")  
        elif index == 1:
            second = int(params[index], 10)
            if second < 0:
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")  
        elif index == 2:
            millisecond = int(params[index], 10)
            if millisecond <0 or millisecond > 1000:
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")  
        else:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    output_str = ''
    if option == 'r':
        time_value = time.time()
        output_str = "%0.3f"%(time_value)
        output_str = output_str.replace('.',',')
        return utility.handle_done(output_str)
    elif option == 'w':
        utc_set_second = second
        utc_set_millisecond = millisecond
        time_str = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(utc_set_second)))
        
        instruction = 'date -s "'
        instruction = instruction + time_str + '"'

        os.system(instruction)
        os.system('touch /opt/seeing/app/handles/tag')
        
        systerm_page = Axi4Sysreg('/dev/AXI4_SYSREG')
        systerm_page.uct_set(utc_set_second, utc_set_millisecond)
        return utility.handle_done()

    else:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")  
            
global mcu_flag
global fpga_flag
global sfpga_flag
mcu_flag = -1
fpga_flag = -1
sfpga_flag = -1
@utility.timeout(1)
def reset_handle(params):
    help_info = "reset({<Name>},{<Flag>)$\r\n\
\tName: (MCU,FPGA,SFPGA)$\r\n \
\tFlag:(0,1)\r\n"

    ''' default operation  '''
    global mcu_flag
    global fpga_flag
    global sfpga_flag 
    operation = 0

    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    ''' parametr analysis '''
    params_count = len(params)
    if params_count != 2:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")  
    
    for index in range(0, params_count):
        if index == 0:
            name = params[index]
            if not(name == 'MCU'  or name == 'FPGA' or name == 'SFPGA'):
                return  utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")  
            
        elif index == 1:
            temp_value =  int(params[index], 10)
            if not (temp_value == 0 or temp_value == 1):
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")  
            
            if name == 'MCU':
                if mcu_flag == 0 and temp_value == 1:
                    os.system('reboot')
                elif mcu_flag == -1 and temp_value == 0:
                    mcu_flag = 0
                    return utility.handle_done("Confirm")
                elif temp_value == 0:
                    return utility.handle_done("Confirm")
                else:
                    return utility.handle_error(utility.handle_errorno['handle_errno_no_permission'],"Confirm first")
                    
            elif name == 'FPGA':
                if fpga_flag == 0 and temp_value == 1:
                    os.system('reboot')
                elif fpga_flag == -1 and temp_value == 0:
                    fpga_flag = 0
                    return utility.handle_done("Confirm")
                elif temp_value == 0:
                    return utility.handle_done("Confirm")
                else:
                    return utility.handle_error(utility.handle_errorno['handle_errno_no_permission'],"Confirm first")
                    
            elif name == 'SFPGA':
                if sfpga_flag == 0 and temp_value == 1:
                    os.system('reboot')
                elif sfpga_flag == -1 and temp_value == 0:
                    sfpga_flag = 0
                    return utility.handle_done("Confirm")
                elif temp_value == 0:
                    return utility.handle_done("Confirm")
                else:
                    return utility.handle_error(utility.handle_errorno['handle_errno_no_permission'],"Confirm first")
                    
        else:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param invalid")  
    
    return utility.handle_done() 

@utility.timeout(1)
def barcode_handle(params):
    help_info = "barcode({<-option>},{<\"serila-number\">)$\r\n\
\toption: (r,w)$\r\n \
\tserila-number:(""), option:w exsit,no content \" \"\r\n"
    
    ''' default operation  '''
    operation = 'r'
    base_param_index = 0

    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    '''  params analysis '''
    option= params[base_param_index]
    if option[base_param_index] == '-':
        if len(option) == 2:
            operation = option[1]
            if not (operation == 'r' or operation == 'w'):
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
            base_param_index = 1
        else:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
    
    param_count = len(params)
    if param_count > 2:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    if operation == 'w':
        serila_number= params[base_param_index]
        if len(serila_number) > 32:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")
    return utility.handle_done()

@utility.timeout(1)
def sn_handle(params):
    help_info = "sn({<-option>},{<\"serila-number\">)$\r\n\
\toption: (r,w)$\r\n \
\tserila-number:(""), option:w exist,no content \" \"\r\n"
    
    ''' default operation  '''
    operation = 'r'
    base_param_index = 0

    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)

    '''  params analysis '''
    option= params[base_param_index]
    if option[base_param_index] == '-':
        if len(option) == 2:
            operation = option[1]
            if not (operation == 'r' or operation == 'w'):
                return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
            base_param_index = 1
        else:
             return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
    
    param_count = len(params)
    if param_count > 2:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")
    
    if operation == 'w':
        serila_number= params[base_param_index]
        if len(serila_number) > 32:
            return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param  error")
    return utility.handle_done()

def arm_delay_handle(params):
    help_info = "arm delay(<millisecond>ms)$\r\n\
\tmillisecond: (1-10000)\r\n"

    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    delay = int(params[0], 10)
    if not(delay >= 1 or delay <= 10000):
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
    
    time.sleep(delay/1000)
    
    return utility.handle_done()

@utility.timeout(1)
def fpga_utc_read_handle(params):
    help_info = "utc read()$\r\n"
    
    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    
    systerm_page = Axi4Sysreg("/dev/AXI4_SYSREG")
    time = systerm_page.uct_get()
    #return utility.handle_done(str(time)[1:(len(str(time)) - 1)])
    return utility.handle_done(str(time))

@utility.timeout()
def update_handle(params):
    help_info = "update(<mode>)$\r\n\
\t mode:(check,clean)$\r\n\
\t    check: check the update file. default:mode=check$\r\n\
\t    clean: clean the update folder"

    mode = "check"

    ''' help '''    
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    if len(params) == 1:
        mode = params[0] 
    elif len(params) > 1:
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
    
    if mode != "clean" and mode != "check":
        return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'],"param error")
    
    if mode == "clean":
        os.chdir("/opt/seeing/tftpboot")
        os.system("rm * ")
        return utility.handle_done()
    
    result = ""
    count = 0
#    update_file_string
    update_file = ''
    for parent, dirnames,filenames in os.walk(update_file_path):
        for filename in filenames:
            if update_file_string in filename:
                update_file  = filename
                result += filename
                result += "\r\n"
                count += 1
            
    if count > 1:
        return utility.handle_error(utility.handle_errorno['handle_errno_crc_checksum_failure'],\
                                    "too many update file\r\n" + result)
    elif count <= 0:
        return utility.handle_done( "no update file")
    
    # check the file md5sum
    os.chdir("/opt/seeing/tftpboot")
    os.system("mkdir checkfile")
    command_string = "tar zxvfm "
    command_string += update_file 
    command_string += " -C checkfile"
    os.system(command_string)
    os.chdir("checkfile")
    res = os.system("md5sum -c md5.txt")   
    if(res != 0):
        return utility.handle_error(utility.handle_errorno['handle_errno_crc_checksum_failure'],\
                                    "md5 check file error")
    return utility.handle_done(update_file + " ok")
'''    
def update_check_handle(params):
    help_info = "update check()$\r\n"
    # help     
    if utility.is_ask_for_help(params) is True:
        return utility.handle_done(help_info)
    pass
'''

@utility.timeout(1)
def test_timeout_handle(params):
    time.sleep(2)

#end of the system file

