#-*- coding: UTF-8 -*-
import traceback
import subprocess
import os
import json
import re
import os.path
from collections import OrderedDict
from ee.profile.profile import Profile
from ee.common import logger
from ee.common import net
from ee.common import utility
import ee.overlay.extendio as Extendio
import ee.overlay.exgpio as Exgpio
from ee.profile.xobj import XObject

def _create_chip_object():
    ret_value = True
    for chip_name, profile in Profile.get_chips().iteritems():
        try:
            partno = profile['partno']
            if XObject.create_object(chip_name, partno, profile):
                logger.boot('create the %s chip object %s'%(chip_name, partno))
            else:
                logger.boot('warning: can not find the %s chip class %s in this project code'%(chip_name, partno))
                ret_value = False
        except Exception as e:
            logger.boot('error: create %s chip object fail:\n%s'%(chip_name, traceback.format_exc()))
            ret_value = False
    return ret_value
            
def _create_board_object():
    ret_value = True
    for board_name, board_profile in Profile.get_boards().iteritems():
        try:
            class_name = board_profile['partno'].replace('-','')
            if XObject.create_object(board_name, class_name, board_profile):
                logger.boot('create the %s board object %s'%(board_name,class_name))
            else:
                logger.boot('warning: can not find the %s board class %s in this project code'%(board_name,class_name))
                ret_value = False
        except Exception as e:
            logger.boot("error: create %s board object fail:\n%s"%(board_name, traceback.format_exc()))
            ret_value = False
    return ret_value

def _create_uart_object():
    ret_value = True
    for bus_name, bus in Profile.get_buses().iteritems():
        try:
            if bus['bus'] == 'uart':
                device_path = bus['path']
                if utility.mount_on_fpga(device_path):
                    class_name = 'Axi4Uart'
                    createok = XObject.create_object(bus_name, class_name, device_path)
                else:
                    class_name = 'UartBus'
                    createok = XObject.create_object(bus_name, class_name, device_path)

                if createok:
                    logger.boot("create the %s uart object %s"%(bus_name, class_name))
                else:
                    logger.boot("warning: can not find the %s uart class %s in this project code"%(bus_name, class_name))
                    ret_value = False
        except Exception as e:
            logger.boot("error: create %s uart object fail:\n%s"%(bus_name , traceback.format_exc()))
            ret_value = False
    return ret_value

def _get_network_num():
    profile = Profile.get_initconfig()
    if profile.has_key("netconfig"):
        net.network_config(profile["netconfig"])
        if profile["netconfig"].has_key("netio"):
            bit_dict = OrderedDict()
            net_num = 0
            index = 0
            bit_list = []
            net_ioes=[]
            if "board_id" not in profile["netconfig"]["netio"] and "path" not in profile["netconfig"]["netio"]:
                if profile["netconfig"]["netio"].has_key("io"):
                    for io in profile["netconfig"]["netio"]["io"]:
                        net_ioes.append(io['bit'])
                    try:
                        bit_dict = Extendio.get(Profile.get_extendio_by_name(), net_ioes)
                        if bit_dict is False:
                            return -1
                    except Exception:
                        return -1
                    for key,value in bit_dict.items():
                        net_num = value << index | net_num 
                        index += 1
                    return net_num

            if "board_id" in profile["netconfig"]["netio"]:
                board_id = profile["netconfig"]["netio"]["board_id"]
                for io in profile["netconfig"]["netio"]["io"]:
                    net_ioes.append(io['bit'])
                try:
                    bit_dict = Extendio.get(Profile.get_extendio_by_name(board_id), net_ioes)
                    if bit_dict is False:
                        return -1
                except Exception:
                    return -1
                for key,value in bit_dict.items():
                    net_num = value << index | net_num 
                    index += 1
                return net_num

            if "path" in profile["netconfig"]["netio"]:
                gpio_input=[]
                path = profile["netconfig"]["netio"]["path"]
                for io in profile["netconfig"]["netio"]["io"]:
                    regular_expression = re.match( r'ch(\w+)_(\w+)', io["bit"])
                    if regular_expression is None:
                        logger.error('_init_net error, please check %s. '%io)
                        return -1
                    else:
                        bit_number_1 = int(regular_expression.group(1), 10)
                        bit_number_2 = int(regular_expression.group(2), 10)
                        bit_number = bit_number_1 * 32 + bit_number_2
                        gpio_input.append((bit_number,255))
                try:
                    bit_list = Exgpio.get(path, gpio_input)
                    for value in bit_list:
                        net_num = value[1] << index | net_num 
                        index += 1
                except Exception:
                    return -1
                return net_num
            else:
                return 0
        else:
            return 0
    else:
        return 0

def _write_default_net():
    net_num = _get_network_num()
    if net_num == -1:
        logger.boot('_init_net. get profile netio state error.')
        net_information_dict = net.read_network_information()
        if "user" == net_information_dict["mode"]:
            net.write_network_information("default:ip", net_information_dict["PowerOn"]["ip"])
            net.write_network_information("default:mac", net_information_dict["PowerOn"]["mac"])
            net.write_network_information("default:mask", net_information_dict["PowerOn"]["mask"])
            net.write_network_information("default:gateway", net_information_dict["PowerOn"]["gateway"])
            logger.boot('_init_net. read user modele and use user ip')
            return True

        with open(utility.get_config_path() + "/network.sh", 'w') as f:
            f.write(net.get_default_network_str())

        os.system("%s/network.sh PowerOn > /dev/null"%(utility.get_config_path()))
        logger.boot('_init_net false, use exceptional ip:%s'%net.exceptional_ip)
        return False

    ip_list = net.default_ip.split(".")
    mac_list=net.default_mac.split(":")
    ip_num = int(ip_list[3]) + int(net_num)
    if ip_num > 254:
        ip_str = net.exceptional_ip
    else:
        del ip_list[3]
        ip_str = ".".join(ip_list) + '.' + str(ip_num)

    if net.set_network_information("default:ip", ip_str) == False:
        return False

    mac_num = int(mac_list[5].upper(),16) + int(net_num)
    if mac_num > 254:
        mac_str=net.exceptional_mac
    else:
        del mac_list[5]
        mac_num=str(hex(mac_num))[2:]
        mac_str = ":".join(mac_list) + ":" + mac_num
    if net.set_network_information("default:mac", mac_str) == False:
        return False

    if net.set_network_information("default:mask", net.default_mask) == False:
        return False
    if net.set_network_information("default:gateway", net.default_gateway) == False:
        return False
    
    logger.boot("_init_net write default network information in network.sh success.,ip:%s, mac:%s." %(ip_str, mac_str))
    return True

def _init_net():
    if False == os.path.exists(utility.get_config_path() + "/network.sh"):
        os.system("mkdir  %s -p  > /dev/null" %(utility.get_config_path()))
        os.system("touch %s/network.sh  > /dev/null"%(utility.get_config_path()))
        os.system("chmod 775 %s/network.sh  > /dev/null"%(utility.get_config_path()))
        with open(utility.get_config_path() + "/network.sh", 'w') as f:
            f.write(net.get_default_network_str())

    if False == _write_default_net():
        logger.boot("_init_net write default network false.")
        return False
    net_information_dict = net.read_network_information()
    
    if net.set_network() is False:
        logger.boot("_init_net set_network Failed.")
    else:
        logger.boot("_init_net set_network Success.")

    network_ip = net_information_dict[net_information_dict["mode"]]["ip"]
    get_ip = "ifconfig |egrep \'[1-9]+\.[1-9]+\.[0-9]+\.[0-9]+\'|awk -F: \'{print $2}\' |cut -d \" \" -f1|sed -n \'1p\'"
    result = subprocess.Popen(get_ip, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    strout,strerr = result.communicate()
    strout = strout.strip('\n')
    if strout != network_ip:
        logger.boot("_init_net network phy is malfunctioning, try to set network again.")
        os.system("%s/network.sh "%(utility.get_config_path())) 

    return True
    
def _init_extendio():
    ret_value = True
    extendios = Profile.get_extendio()
    initconfig = Profile.get_initconfig()
    
    for board_name, extendio_profile in extendios.iteritems():
        for chip_name,bit in initconfig['extendio'][board_name].iteritems():
            try:
                partno = extendio_profile[chip_name]['partno']
                if Extendio.chip_set(extendio_profile, chip_name, bit['value']) is True:
                    ret = Extendio.chip_dir_set(extendio_profile, chip_name, bit['dir'])
                    if ret is False:
                        logger.boot('error: set the %s board %s chip %s value:%s fail'
                                    %(board_name,partno,chip_name,logger.print_list2hex(bit['value'])))
                        ret_value = False
                    else:
                        logger.boot('init the %s board extendio chip %s success, value is %s, direction is %s'
                                %(board_name,chip_name,logger.print_list2hex(bit['value']),logger.print_list2hex(bit['dir'])))
                else:
                    logger.boot('error: set the %s board %s chip %s direction:%s fail'
                            %(board_name,partno,chip_name, logger.print_list2hex(bit['dir'])))
                    ret_value = False

            except Exception:
                logger.boot("error: %s _init_extendio execute error:\n%s"%(chip_name,traceback.format_exc()))
                ret_value = False

    return ret_value

def _init_board():
    ret_value = True
    initconfig = Profile.get_initconfig()
    
    for board_name in initconfig['boards']:
        try:
            obj = XObject.get_board_object(board_name)
            if obj is None:
                logger.boot('warning: can not find the %s object'%(board_name))
                continue
        
            if obj.board_initial():
                logger.boot('init the %s board success'%(board_name))
            else:
                logger.boot('error: init the %s board fail'%(board_name))
                ret_value = False
        except Exception:
            logger.boot('error: %s _init_board execute error:\n%s'%(board_name, traceback.format_exc()))
            ret_value = False
            
    return ret_value

def _init_uart():
    ret_value = True
    initconfig = Profile.get_initconfig()

    for name ,param in initconfig['uart'].iteritems():
        try:
            obj = XObject.get_object(name)
            if obj is None:
                logger.boot("warning: can not find the %s uart object"%(name))
                continue

            baudrate = int(param['baudrate'])
            databits = int(param['databits'])
            stopbits = int(param['stopbits'])
            parity = param['parity'].upper()
            if utility.mount_on_fpga(obj.name):
                timestamp = param['timestamp'].upper()
                obj.disable()
                obj.enable()
                ret = obj.config(baudrate, databits, parity, stopbits, timestamp)
            else:
                ret = obj.config(baudrate, databits, parity, stopbits)
            if ret is False:
                logger.boot("error: init the %s uart param:%s fail"%(name, param))
                ret_value = False
            else:
                logger.boot("init the %s uart success, param:%s"%(name, param))
        except Exception as e:
            logger.boot("error: %s _init_uart execute error:\n%s"%(name, traceback.format_exc()))
            ret_value = False

    return ret_value

def _init_gpio():
    ret_value = True
    initconfig = Profile.get_initconfig()
    digital_io = Profile.get_ioes()
    if 'gpio' in initconfig.keys():
        for io_id,param in initconfig['gpio'].iteritems():
            try:
                device_path = digital_io[io_id]['path']
                if Exgpio.dir_set(device_path,(param['dir'],)) is not False:
                    logger.boot('set the %s gpio number %s direction:%s success'%(io_id,param['dir'][0],param['dir'][1]))
                    if 'value' in param.keys():
                        if Exgpio.set(device_path,(param['value'],)) is not False:
                            logger.boot('set the %s gpio number %s value:%s success'%(io_id,param['value'][0],param['value'][1]))
                        else:
                            logger.boot('warning: set the %s gpio number %s value:%s fail'%(io_id,param['value'][0],param['value'][1]))
                            ret_value = False
                else:
                    logger.boot('warning the %s gpio number %s direction:%s fail'%(io_id,param['dir'][0],param['dir'][1]))
                    ret_value = False
            except Exception as e:
                logger.boot("error: %s _init_gpio execute error:\n%s"%(io_id, traceback.format_exc()))
                ret_value = False
    return ret_value

def init():
    initok = True
    logger.boot('start init')

    if _create_uart_object() is False:
        initok = False

    if _create_chip_object() is False:
        initok = False
        
    if _create_board_object() is False:
        initok = False

    initconfig = Profile.get_initconfig()

    #init gpio
    if _init_gpio() is False:
        initok = False

    #init uart
    if initconfig.has_key('uart'):
        if _init_uart() is False:
            initok = False

    #initexitendio
    if initconfig.has_key('extendio'):
        if _init_extendio() is False:
            initok = False

    #init board
    if initconfig.has_key('boards'):
        if _init_board() is False:
            initok = False

    #init net
    try:
        if _init_net() is False:
            initok = False
    except Exception as e:
        logger.boot("error: _init_net execute error:\n%s"%(traceback.format_exc()))
        initok = False

    if not initok:
        logger.boot('error: init project fail')
    else:
        logger.boot("init project done")
        
    return initok
