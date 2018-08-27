# -*- coding:utf-8 -*-
import os
import re
import ctypes
import json

def list_convert_number(data_list):
    byte_number = data_list.__len__()
    
    if byte_number == 1:
        return data_list[0]
    if byte_number == 2:
        return data_list[1] << 8 | data_list[0]
    if byte_number == 3:
        return data_list[2] << 16 | data_list[1] << 8 | data_list[0]
    if byte_number == 4:
        return data_list[3] << 24 | data_list[2] << 16 | data_list[1] << 8 | data_list[0]
    if byte_number == 8:
        return data_list[7] << 56 | data_list[6] << 48 | data_list[5] << 40 | data_list[4] << 32 | \
                      data_list[3] << 24 | data_list[2] << 16 | data_list[1] << 8 | data_list[0]
    
    return False

def int_convert_list(int_data,list_len):
    list_out = []
    for i in range (0,list_len):
        list_out.append(int_data%256)
        int_data = int_data >> 8
    return list_out     

def mount_on_fpga(name):
    return re.search("AXI4_", name)

def get_lib_path():
    return os.environ.get('XAVIER_LIB_PATH', "/opt/seeing/app/lib")

def get_libci2cbus_name():
    return os.environ.get('XAVIER_LIB_PSI2C')

def get_profile_path():
    return os.environ.get('XAVIER_PROFILE_PATH', "/opt/seeing/app/ee/profile")

def get_pid_path():
    return os.environ.get('XAVIER_PID_PATH', "/opt/seeing/pid")
    
def get_config_path():
    return os.environ.get('XAVIER_CONFIG_PATH', "/opt/seeing/config")

def get_log_path():
    return os.environ.get("XAVIER_LOG_PATH", "/opt/seeing/log")

def get_app_path():
    return os.environ.get("XAVIER_APP_PATH", "/opt/seeing/app")

def get_dev_path():
    return os.environ.get('XAVIER_DEV_PATH', '/dev')

def register_signal_handle():
    lib_name = get_lib_path() + "/libsgutil.so"
    lib_sig = ctypes.cdll.LoadLibrary(lib_name)
    lib_sig.signal_register()


def string_convert_float_value(string_value):
    """get value from string

    Args:
        string_value: string

    Returns:
        if paser success:
            (float,unit)
            eg. 
                input: "-100.3mV"
                return:(-100.3,'mV')
        else:
            None
    """
    matchObj = re.match('([-+]?[0-9]*\.?[0-9]+)(\D*)',string_value)
    if matchObj:
        #print(matchObj.group(1))
        value = float(matchObj.group(1))
        unit = matchObj.group(2)
        return (value,unit)
    else:
        return None

def string_convert_int_value(string_value):
    """get value from string

    Args:
        string_value: string

    Returns:
        if paser success:
            (int,unit)
            eg. 
                input: "-100.3mV"
                return:(-100,'mV')
        else:
            None
    """
    matchObj = re.match('([-+]?[0-9]*\.?[0-9]+)(\D*)',string_value)
    if matchObj:
        # print(matchObj.group(1))
        value = int(float(matchObj.group(1)))
        unit = matchObj.group(2)
        return (value,unit)
    else:
        return None

def string_to_float(string):
    """get value from string

    Args:
        string: string

    Returns:
        if paser success:
            return float value
            eg. 
                input: "-100.3mV"  | "100.3" 
                return:-100.3 |100.3
        else:
            None
    """
    matchObj = re.match('([-+]?[0-9]*\.?[0-9]+)',string)
    if matchObj:
        #print(matchObj.group(1))
        value = float(matchObj.group(1))
        return value
    else:
        return None

def load_json_file(file, encoding = None, cls = None, object_hook = None, parse_float = None, \
                   parse_int = None, parse_constant = None, object_pairs_hook = None, kw = {}):
    json_text = ""
    if True == os.path.isfile(file):
        with open(file) as jsonfile:
            comment_area1 = False
            comment_area2 = False
            for line in jsonfile.readlines():
                if (line.strip()[:3] == "'''") and (comment_area1 == False) and (comment_area2 == False):
                    comment_area1 = True
                    continue
                elif (line.strip()[:3] == "'''") and (comment_area1 == True) and (comment_area2 == False):
                    comment_area1 = False
                    continue
                elif (line.strip()[:3] == "\"\"\"") and (comment_area1 == False) and (comment_area2 == False):
                    comment_area2 = True
                    continue
                elif (line.strip()[:3] == "\"\"\"") and (comment_area1 == False) and (comment_area2 == True):
                    comment_area2 = False
                    continue
                elif (comment_area1 == True) or (comment_area2 == True):
                    continue
                elif (line.strip()[:1] == "#"):
                    continue
                elif (line.strip()[:2] == "//"):
                    continue
                json_text = json_text + line.strip()

    if json_text:
        load_json = json.loads(json_text, encoding, cls, object_hook, parse_float, parse_int, parse_constant, object_pairs_hook, **kw)
    else:
        load_json = {}

    return load_json