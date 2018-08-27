import re
import time
import json
import os
import os.path
import sys
import subprocess
import commands
from ee.common import logger
from ee.common import utility
from ee.common import xavier as Xavier

dfu_server_process = "/opt/seeing/app/packages/dfuserver/dfu_rpc_server "

_g_dfu_logger_level_dict = {
    "LOG_LEVEL_INIT" : 0x01,
    "LOG_LEVEL_FATAL": 0x02,
    "LOG_LEVEL_ERROR": 0x04,
    "LOG_LEVEL_WARNING": 0x08,
    "LOG_LEVEL_INFO": 0x10,
    "LOG_LEVEL_DEBUG": 0x20
    }
_g_dfu_logger_type_dict = {
    "LOG_FILE" : 0x0100,
    "LOG_UDP_BOARDCAST" : 0x0200,
    "LOG_TCP" : 0x0400,#do not realize
    "LOG_UDEF": 0x0800,#do not know
    }

def setup_fwdl_rpc_server(argv):
    fwdl_config_list = utility.load_json_file("/opt/seeing/app/fwdl_config/Fwdl_Profile.json")
    monitor_config_list = utility.load_json_file("/opt/seeing/app/fwdl_config/Fwdl_Profile.json")
    
    #start server
    for channel in fwdl_config_list["support_channel"].keys():
        if(argv[1] == channel):
            os.system("mkdir -p "+fwdl_config_list["support_channel"][channel]["firmware_path"])
            ip = fwdl_config_list["support_channel"][channel]["rpc_server_config"]["ip"]
            port = fwdl_config_list["support_channel"][channel]["rpc_server_config"]["port"]
            process_name = fwdl_config_list["support_channel"][channel]["rpc_server_config"]["name"]
            dfu_rpc_config = ip+" "+str(port)+" "+process_name
            #kill the process first
            
            result = subprocess.Popen("ps -aux | awk '{print $11}' | grep ^%s$"%(process_name), \
                                   shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
            result = re.split(r"\n",result[0])[0]
            #if running
            if result == process_name:
                os.system("killall -9 "+process_name)
                print("kill the target process first ")
            time.sleep(0.1)
            
            #then start the server
            subprocess.Popen(dfu_server_process+dfu_rpc_config,shell=True)
    
            print("run the target process")
            time.sleep(0.1)#wait rpc process runing
    
            #check the dfu rpc server if running or not
            result = subprocess.Popen("ps -aux | awk '{print $11}' | grep ^%s$"%(process_name), \
                                   shell=True,stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
            result = re.split(r"\n",result[0])[0]
            #if running
            if result == process_name:
                print("true")
            else:
                print("process is not running")
                return False
            break
        pass
    
    #configure the dfu rpc server 
    for channel in fwdl_config_list["support_channel"].keys():
        if(argv[1] == channel):
            print("this is "+channel+" configure")
            ip = fwdl_config_list["support_channel"][channel]["rpc_server_config"]["ip"]
            port = fwdl_config_list["support_channel"][channel]["rpc_server_config"]["port"]
            process_name = fwdl_config_list["support_channel"][channel]["rpc_server_config"]["name"]
            
            for log_param in fwdl_config_list["support_channel"][channel]["rpc_server_config"]["log"]:
                param = {}
                time.sleep(1)#wait rpc process runing
                if (log_param["type"] in _g_dfu_logger_type_dict.keys()) and (log_param["log_level"] in _g_dfu_logger_level_dict.keys()):
                    if log_param["type"] == "LOG_FILE":
                        param["file_path"] = str(log_param["path"])
                        param["type_level"] = _g_dfu_logger_level_dict[log_param["log_level"]]|_g_dfu_logger_type_dict[log_param["type"]]
                        dfu_rpc_node = Xavier.XavierRpcClient(ip,port,"tcp")
                        ret = dfu_rpc_node.call("LoggerInitial",**param)
                        print(ret)
    
                    elif log_param["type"] == "LOG_UDP_BOARDCAST":
                        param["net_type"] = 0#udp boardcast
                        param["port"] = str(log_param["port"])
                        param["type_level"] = _g_dfu_logger_level_dict[log_param["log_level"]]|_g_dfu_logger_type_dict[log_param["type"]]
                        dfu_rpc_node = Xavier.XavierRpcClient(ip,port,"tcp")
                        ret = dfu_rpc_node.call("LoggerInitial",**param)
                        print(ret)
                    else:
                        logger.error("error not support this log type !")
                        #error not support this log
                        pass
                pass
            break
#         param["type_level"] = 0x20|0x100|0x200#logger debug,file,udp
#         param["file_path"] = "/opt/seeing/log/"+process_name+".log"
#         param["net_type"] = 0#udp boardcast
#         param["port"] = str(port)
#         
#         dfu_rpc_node = Xavier.XavierRpcClient(ip,port,"tcp")
#         ret = dfu_rpc_node.call("LoggerInitial",**param)
#         print(ret)

    return True


def reset_fwdl_rpc_server(process_name):
    config_fp = open("/opt/seeing/app/projects/fwdl_config/Fwdl_Profile.json",encoding='utf-8')
    #read the profile json
    fwdl_config_list = json.load(config_fp)
    config_fp.close()
    
    
    
    
    
    return True


def main(argv):
#     if argv[1] == "setup":
    ret = setup_fwdl_rpc_server(argv)
    if ret == False:
        print("dfu server error setup!")
    pass
#     elif argv[1] == "reset":
#         process_name = argv[2]
#         reset_fwdl_rpc_server(process_name)
#         pass
    
    pass


if __name__=="__main__":
    main(sys.argv)


