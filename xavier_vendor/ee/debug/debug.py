#-*- coding: UTF-8 -*-
import os
import sys
sys.path.append('/opt/seeing/app')
import json
from time import sleep
from ee.common import logger

#此处导入模块
#from buses.axi4lite import Axi4lite    # example
from ee.board.se2625bp01pc import SE2625BP01PC

profile={
            "partno": "SE2625-BP01PC", "id": "bp", 
            "dac1": {"partno": "AD5667", "id": "bp", "addr": "0x0c", "bus": "ps_i2c_1", "switch_channel": "none", "vref": "5500mv"},
            "dac2": {"partno": "AD5667", "id": "bp", "addr": "0x0f", "bus": "ps_i2c_1", "switch_channel": "none", "vref": "5500mv"},
            "dac3": {"partno": "AD5667", "id": "bp", "addr": "0x0e", "bus": "ps_i2c_1", "switch_channel": "none", "vref": "5500mv"},
            "eeprom": {"partno": "AT24C08", "id":"bp","bus": "ps_i2c_1", "switch_channel": "none","addr": "0x54"},
            "frequency":{"path": "AXI4_Signal_Meter_0", "id":"bp","ipcore": "Axi4SignalMeter","samplerate":"100000000Hz"},
            "adc":{"partno": "AD7608","path": "AXI4_AD760x_0", "id":"bp","ipcore": "axi4_ad760x"},
        }

def init():
    config_file = open('sepyd.json')
    data = json.load(config_file)
    os.environ['ARM_BOARD_IP'] = data['ArmBoardIP']
    

if __name__=="__main__":
    logger.init("debug.log")
    logger.setLevel('debug')
    init()
    
    #此处调用调试代码
device = SE2625BP01PC(profile)
device.adc7608_read('-v','nor','A','10V',1)

        
    

    
    
    
    
    

    
