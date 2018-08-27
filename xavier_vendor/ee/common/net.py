# -*- coding:utf-8 -*-
import os
import json
import re
import subprocess
import time
from ee.common import utility
from ee.common import logger

global exceptional_ip
global exceptional_gateway
global default_ip
global default_gateway
global default_mask

exceptional_ip="192.168.99.10"
exceptional_mac="02:0a:35:00:01:10"
exceptional_gateway="192.168.99.1"
exceptional_mask="255.255.255.0"

default_ip="192.168.99.11"
default_mac="02:0a:35:00:01:11"
default_gateway="192.168.99.1"
default_mask="255.255.255.0"

def get_default_network_str():
    """   Get network scripts string .
            You can use its return value to write into network.sh file.
        Args:
                None
            
        Returns:  str type.
            
    """
    default_network="#!/bin/bash\n\
mode=default\n\
[ $# -ge 1 ] && mode=PowerOn\n\
if [ \"$mode\" == \"PowerOn\" ];then\n\
    ifconfig eth0 down\n\
    ifconfig eth0 hw ether " + exceptional_mac + "\n\
    ifconfig eth0 up\n\
    ifconfig eth0 "+exceptional_ip + "\n\
    ifconfig eth0 netmask "+ exceptional_mask + "\n\
    route add default gw " +exceptional_gateway + "\n\
elif [ \"$mode\" == \"user\" ];then\n\
    ifconfig eth0 down\n\
    ifconfig eth0 hw ether " +default_mac + "\n\
    ifconfig eth0 up\n\
    ifconfig eth0 "+ default_ip + "\n\
    ifconfig eth0 netmask " +default_mask + "\n\
    route add default gw " +default_gateway + "\n\
elif [ \"$mode\" == \"default\" ];then\n\
    ifconfig eth0 down\n\
    ifconfig eth0 hw ether " +default_mac + "\n\
    ifconfig eth0 up\n\
    ifconfig eth0 " +default_ip + "\n\
    ifconfig eth0 netmask " +default_mask + "\n\
    route add default gw " +default_gateway + "\n\
fi\n"
    return default_network

def network_config(netconfig):
    ''' Change the global variable
        
        Args:
            Dict type. Keys can be comprised of  "start_ip" "mask" and "exceptional_ip".
            eg: {
                    "start_ip": "192.168.99.40",
                    "mask": "255.255.255.0",
                    "exceptional_ip": "192.168.99.30"
                    }

        Returns: None

    '''
    global exceptional_ip
    global exceptional_gateway
    global default_ip
    global default_gateway
    global default_mask

    if netconfig.has_key("start_ip") and netconfig["start_ip"] != "":
        default_ip = netconfig["start_ip"]
        ip_list = default_ip.split(".")
        ip_list[3] = "1"
        default_gateway = ".".join(ip_list)

    if netconfig.has_key("mask") and netconfig["mask"] != "":
        default_mask = netconfig["mask"]
        
    if netconfig.has_key("exceptional_ip") and netconfig["exceptional_ip"] != "":
        exceptional_ip = netconfig["exceptional_ip"]
        ip_list = exceptional_ip.split(".")
        ip_list[3] = "1"
        exceptional_gateway = ".".join(ip_list)
        write_network_information("PowerOn:ip", exceptional_ip)
        write_network_information("PowerOn:gateway", exceptional_gateway)

def write_network_information(net_field, net_information):
    ''' write network Configuration information into network.sh file.
        
        Args:
            net_field: str type, format: "mode" or "xx:YY"
                            "mode": net_information must be "user" "default" or "PowerOn"
                            "xx": "user" "default" or "PowerOn"
                            "YY":"ip" "mac" "gateway" or "mask"
                            eg: "user:ip"

            net_information: str type. 

        Returns: None

    '''
    network_file = utility.get_config_path() + "/network.sh"
    net_information_dict = read_network_information()
    fields = net_field.split(":")
    if (1 == len(fields)):
        net_information_dict["mode"] = net_information

    else:
        if "user" == fields[0]:
            if "ip" == fields[1]:
                net_information_dict["user"]["ip"] = net_information
            if "mac" == fields[1]:
                net_information_dict["user"]["mac"] = net_information
            if "gateway" == fields[1]:
                net_information_dict["user"]["gateway"] = net_information
            if "mask" == fields[1]:
                net_information_dict["user"]["mask"] = net_information

        elif "default" == fields[0]:
            if "ip" == fields[1]:
                net_information_dict["default"]["ip"] = net_information
            if "mac" == fields[1]:
                net_information_dict["default"]["mac"] = net_information
            if "gateway" == fields[1]:
                net_information_dict["default"]["gateway"] = net_information
            if "mask" == fields[1]:
                net_information_dict["default"]["mask"] = net_information

        else:
            if "ip" == fields[1]:
                net_information_dict["PowerOn"]["ip"] = net_information
            if "mac" == fields[1]:
                net_information_dict["PowerOn"]["mac"] = net_information
            if "gateway" == fields[1]:
                net_information_dict["PowerOn"]["gateway"] = net_information
            if "mask" == fields[1]:
                net_information_dict["PowerOn"]["mask"] = net_information
        
    net_information_str = "#!/bin/bash\n"
    net_information_str = net_information_str + "mode=%s\n"%net_information_dict["mode"]
    net_information_str = net_information_str + '[ $# -ge 1 ] && mode=PowerOn\n'

    net_information_str = net_information_str + "if [ \"$mode\" == \"PowerOn\" ];then\n"
    net_information_str = net_information_str + '    ifconfig eth0 down\n'
    net_information_str = net_information_str + '    ifconfig eth0 hw ether ' + '%s\n'%net_information_dict["PowerOn"]["mac"]
    net_information_str = net_information_str + '    ifconfig eth0 up\n'
    net_information_str = net_information_str + '    ifconfig eth0 ' + '%s\n'%net_information_dict["PowerOn"]["ip"]
    net_information_str = net_information_str + '    ifconfig eth0 netmask ' + '%s\n'%net_information_dict["PowerOn"]["mask"]
    net_information_str = net_information_str + '    route add default gw ' + '%s\n'%net_information_dict["PowerOn"]["gateway"]    

    net_information_str = net_information_str + "elif [ \"$mode\" == \"user\" ];then\n"
    net_information_str = net_information_str + '    ifconfig eth0 down\n'
    net_information_str = net_information_str + '    ifconfig eth0 hw ether ' + '%s\n'%net_information_dict["user"]["mac"]
    net_information_str = net_information_str + '    ifconfig eth0 up\n'
    net_information_str = net_information_str + '    ifconfig eth0 ' + '%s\n'%net_information_dict["user"]["ip"]
    net_information_str = net_information_str + '    ifconfig eth0 netmask ' + '%s\n'%net_information_dict["user"]["mask"]
    net_information_str = net_information_str + '    route add default gw ' + '%s\n'%net_information_dict["user"]["gateway"]
    
    net_information_str = net_information_str + 'elif [ \"$mode\" == \"default\" ];then\n'
    net_information_str = net_information_str + '    ifconfig eth0 down\n'
    net_information_str = net_information_str + '    ifconfig eth0 hw ether ' + '%s\n'%net_information_dict["default"]["mac"]
    net_information_str = net_information_str + '    ifconfig eth0 up\n'
    net_information_str = net_information_str + '    ifconfig eth0 ' + '%s\n'%net_information_dict["default"]["ip"]
    net_information_str = net_information_str + '    ifconfig eth0 netmask ' + '%s\n'%net_information_dict["default"]["mask"]
    net_information_str = net_information_str + '    route add default gw ' + '%s\n'%net_information_dict["default"]["gateway"]
    net_information_str = net_information_str + 'fi'
    
    fp = open(network_file, "w+")
    fp.write(net_information_str)
    fp.close()
    return None

def __set_ip(net_information):
    if net_information:
        ip_str ="ifconfig eth0 " +  net_information
        result = subprocess.Popen(ip_str, shell=True, stderr=subprocess.PIPE)
        strout,strerr = result.communicate()
        if strerr:
            logger.warning("set  net ip:%s Failed."%(net_information))
            return False

def __set_mac(net_information):
    if net_information:
        mac_str ="ifconfig eth0 hw ether  " +  net_information
        result = subprocess.Popen("ifconfig eth0 down", shell=True,stderr=subprocess.PIPE)
        strout,strerr = result.communicate()
        if strerr:
            logger.warning("eth0 down  Failed.")
            return False

        result = subprocess.Popen(mac_str, shell=True,stderr=subprocess.PIPE)
        strout,strerr = result.communicate()
        if strerr:
            logger.warning("set  net MAC:%s Failed."%(net_information))
            return False

        result = subprocess.Popen("ifconfig eth0 up", shell=True,stderr=subprocess.PIPE)
        strout,strerr = result.communicate()
        if strerr:
            logger.warning("eth0 up  Failed.")
            return False

def __set_mask(net_information):
    if net_information:
        mask_str ="ifconfig eth0 netmask  " +  net_information
        result = subprocess.Popen(mask_str, shell=True,stderr=subprocess.PIPE)
        strout,strerr = result.communicate()
        if strerr:
            logger.warning("set mask %s Failed."%(net_information))
            return False

def __set_gateway(net_information):
    if net_information:
        gate_str ="route add default gw  " +  net_information
        result = subprocess.Popen(gate_str, shell=True,stderr=subprocess.PIPE)
        strout,strerr = result.communicate()
        if strerr:
            logger.warning("set gateway %s False."%(net_information))
            return False
    return True

def set_user_network():
    ''' set network in user mode.
        
        Args: None

        Returns: 
            bool type.True for success, False otherwise

    '''
    net_information_dict = read_network_information()

    if (False == __set_mac(net_information_dict["user"]["mac"])):
        return False

    if (False == __set_ip(net_information_dict["user"]["ip"])):
        return False

    if (False == __set_mask(net_information_dict["user"]["mask"])):
        return False

    if (False == __set_gateway(net_information_dict["user"]["gateway"])):
        return False
    return True

def set_default_network():
    ''' set network in default mode.
        
        Args: None

        Returns: 
            bool type.True for success, False otherwise

    '''
    net_information_dict = read_network_information()

    if (False == __set_mac(net_information_dict["default"]["mac"])):
        return False
    if (False == __set_ip(net_information_dict["default"]["ip"])):
        return False
    if (False == __set_mask(net_information_dict["default"]["mask"])):
        return False
    if (False == __set_gateway(net_information_dict["default"]["gateway"])):
        return False
    return True

def set_network_information(net_field, net_information):
    ''' set network information

    Args:
            net_field: str type, format: "mode" or "xx:YY"
                            "mode": net_information must be "user" "default" or "PowerOn"
                            "xx": "user" "default" or "PowerOn"
                            "YY":"ip" "mac" "gateway" or "mask"
                            eg: "user:ip"

            net_information: str type. 

        Returns: None

    '''
    fields = net_field.split(":")

     # change mode

    if (1 == len(fields)):
        if (fields[0] != "mode"):
            return False
        if "default" == net_information:
            if False == set_default_network():
                return False
            write_network_information(net_field, net_information)
            return True
        elif "user" == net_information:
            net_information_dict = read_network_information()

            if net_information_dict["user"]["mac"]:
                mac = net_information_dict["user"]["mac"]
            else:
                mac = net_information_dict["default"]["mac"]
            write_network_information("user:mac", mac)

            if net_information_dict["user"]["ip"]:
                ip = net_information_dict["user"]["ip"]
            else:
                ip = net_information_dict["default"]["ip"]
            write_network_information("user:ip", ip)

            if net_information_dict["user"]["mask"]:
                mask = net_information_dict["user"]["mask"]
            else:
                mask = net_information_dict["default"]["mask"]
            write_network_information("user:mask", mask)

            if net_information_dict["user"]["gateway"]:
                gateway = net_information_dict["user"]["gateway"]
            else:
                gateway = net_information_dict["default"]["gateway"]
            write_network_information("user:gateway", gateway)

            if False == set_user_network():
                return False
            write_network_information(net_field, net_information)
            return True
        else:
            return False


    # change network

    net_information_dict = read_network_information()
    if fields[1] == "ip":
        if net_information_dict["mode"] == fields[0]:
            if (False == __set_ip(net_information)):
                return False

    elif fields[1] == "mac":
        if net_information_dict["mode"] == fields[0]:
            if (False == __set_mac(net_information)):
                return False

    elif fields[1] == "mask":
        if net_information_dict["mode"] == fields[0]:
            if (False == __set_mask(net_information)):
                return False

    elif fields[1] == "gateway":
        if net_information_dict["mode"] == fields[0]:
            if (False == __set_gateway(net_information)):
                return False

    else:
        logger.warning("set network False. not have %s." %fields[1])
        return False

    write_network_information(net_field, net_information)
    return True

def read_network_information():
    ''' read network information from network.sh file.
        
        Args: None

        Returns:
            Dict type.  
                eg: 
                {'mode': 'default', 
                    'default':      {'ip': '169.254.1.32', 'mac': '02:0a:35:00:01:4', 'mask': '255.255.255.0', 'gateway': '169.254.1.1'}, 
                    'PowerOn':  {'ip': '169.254.1.30', 'mac': '02:0a:35:00:01:3', 'mask': '255.255.255.0', 'gateway': '169.254.1.1'}, 
                    'user':          {'ip': '169.254.1.31', 'mac': '02:0a:35:00:01:4', 'mask': '255.255.255.0', 'gateway': '169.254.1.1'}}

    '''
    network_file = utility.get_config_path() + "/network.sh"
    net_information_dict = {}
    net_information_dict["mode"] = ""

    net_information_dict["default"] = {}
    net_information_dict["user"] = {}
    net_information_dict["PowerOn"] = {}

    net_information_dict["default"]["ip"]= ""
    net_information_dict["default"]["mac"]= ""
    net_information_dict["default"]["mask"]= ""
    net_information_dict["default"]["gateway"]= ""

    net_information_dict["user"]["ip"]= ""
    net_information_dict["user"]["mac"]= ""
    net_information_dict["user"]["mask"]= ""
    net_information_dict["user"]["gateway"]= ""

    net_information_dict["PowerOn"]["ip"]= ""
    net_information_dict["PowerOn"]["mac"]= ""
    net_information_dict["PowerOn"]["mask"]= ""
    net_information_dict["PowerOn"]["gateway"]= ""

    mode_state=None
    for line in open(network_file, "r+"):
        module = re.match(r'mode=(\w+)',line)
        if module is not None:
            net_information_dict["mode"] = str(module.group(1))
        
        regular_expression = re.search(r'\[ \"\$mode\" == \"PowerOn\" \]',line)
        if regular_expression:
            mode_state = "PowerOn"

        regular_expression = re.search(r'\[ \"\$mode\" == \"user\" \]',line)
        if regular_expression:
            mode_state = "user"

        regular_expression = re.search(r'\[ \"\$mode\" == \"default\" \]',line)
        if regular_expression:
            mode_state = "default"

        if mode_state is not None:
            user_ip = re.match(r'    ifconfig eth0 (\w+)\.(\w+)\.(\w+)\.(\w+)',line)
            user_mac = re.match(r'    ifconfig eth0 hw ether (\w+)\:(\w+)\:(\w+)\:(\w+)\:(\w+)\:(\w+)',line)
            user_gate = re.match(r'    route add default gw (\w+)\.(\w+)\.(\w+)\.(\w+)',line)
            user_mask = re.match(r'    ifconfig eth0 netmask (\w+)\.(\w+)\.(\w+)\.(\w+)',line)
            if user_ip is not None:
                net_information_dict[mode_state]["ip"] = ".".join(user_ip.group(1,2,3,4))
            if user_mac is not None:
                net_information_dict[mode_state]["mac"] = ":".join(user_mac.group(1,2,3,4,5,6))
            if user_gate is not None:
                net_information_dict[mode_state]["gateway"] = ".".join(user_gate.group(1,2,3,4))
            if user_mask is not None:
                net_information_dict[mode_state]["mask"] = ".".join(user_mask.group(1,2,3,4))
                
    if net_information_dict["mode"]=="":
        net_information_dict["mode"]="default"
    return net_information_dict

def set_network():
    ''' Use network.sh to set network
        
        Args: None

        Returns:
            bool type.True for success, False otherwise

    '''
    network_file = utility.get_config_path() + "/network.sh"
    set_network_str="/bin/bash "+ network_file
    result = subprocess.Popen(set_network_str, shell=True,stderr=subprocess.PIPE)
    strout,strerr = result.communicate()
    if strerr:
        logger.warning("set_network Failed.")
        return False
    return True
