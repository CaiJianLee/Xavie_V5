"""Datalogger board driver

This board which Born in IA473
Two channel.
function: data upload and current measure

"""
import copy
import sys
import time
import math
#from ee.board.bp288fctzynq.ad7175  import AD7175
from ee.board.b288fctbp.ad7175 import AD7175
import ee.overlay.eeprom as Eeprom
from ee.common import logger
import ee.common.utility as Utility
from ee.profile.profile import Profile
from ee.ipcore. axi4_frame_config import Axi4Frame
#from gi.overrides.keysyms import currency
__version__="1.0"

#Datalogger board hardware description
#Don't change it in the program is running
#For FPGA reasons, the two channels have the same samplerate
_datalogger_board_description={
    "channel":{
        "current":{
            "range":{
                "1A":{
                    "sample_resistor":(0.5,"ohm"),
                    "gain":1.0,
                    "offset":0
                }
            },
            "adc_config":{
                "channel":"chan0",
                "config":{"P":"AIN0","N":"AIN1"},
            }
        },

        "voltage":{
            "range":{
                "2500mV":{
                    "gain":1.0,
                    "offset":0
                }
            },
            "adc_config":{
                "channel":"chan1",
                "config":{"P":"AIN2","N":"AIN3"},
            }
        }
    },
}

"""
'profile': {
    "partno": "Scope-002-001A", 
    "id": "datalogger",                
     "daq_channel":[
            {"type": "datalogger", "ch": 0, "id": "current", "port": 7604, "chipnum": 1, "filters": ["output"]},
            {"type": "datalogger", "ch": 1, "id": "voltage", "port": 7603, "chipnum": 1, "filters": ["output"]}
        ],
    "adc": {"partno": "AD7175", "path": "AXI4_DATALOGGER_AD7177", "samplerate": "1000Hz", "vref": "2500mV", "chipnum": 1},
    "eeprom": {"partno": "CAT24C08", "bus": "EEPROM_IIC", "switch_channel": "Datalogger-1", "addr": "0x53"}
}
"""

class bp288datalogger(object):
    def __init__(self,profile):
        self.profile= profile
        self.chipnum = profile["adc"]["chipnum"]
        self.channels=[]
        for channel in profile["daq_channel"]:
            self.channels.append(channel["id"])

        vref = Utility.string_convert_int_value(profile["adc"]["vref"])
        self.vref = vref
        self.adc_device = AD7175(profile["adc"]["path"],vref)
        self.framer=Axi4Frame(profile["frame_device_path"])
        samplerate = Utility.string_convert_int_value(profile["adc"]["samplerate"])
        self.datalogger_samplerate = samplerate
        self.adc_samplerate={"current":samplerate,
                                                "voltage":samplerate
                                            }
        self.initial_flag = False        #initial flag,success=True,Fail=False

    @staticmethod
    def parse_board_profile(board):
        '''
        "DATALOGGER": {
            "id": "DATALOGGER",
            "partno": "Scope-002-001",
            "daq_channel":[
                {"ch": 0, "alias": "volt", "port": 7603},
                {"ch": 1, "alias": "current", "port": 7604}
            ],
            "adc": {"partno": "AD7175", "path": "/dev/AXI4_DATALOGGER_AD7177"},
            "eeprom": {"partno": "CAT24C08", "bus": "EEPROM_IIC", "switch_channel": "Datalogger-1", "addr": "0x53"}
        }
        '''
        board_name = board['id']
        
        boards = Profile.get_boards()
        boards[board_name] = dict()
        boards[board_name]['id'] = board_name
        boards[board_name]['partno'] = board['partno']
        boards[board_name]['adc'] = board['adc'].copy()
        boards[board_name]['adc']['path'] = Utility.get_dev_path() + '/' + board['adc']['path']
        boards[board_name]['daq_channel'] =copy.deepcopy( board['daq_channel'])
        boards[board_name]['frame_device_path'] = Utility.get_dev_path() + '/' + board['frame_device_path']

    def adc_register_write(self,register,value):
        """ Write data to AD7175 adc register

            Args:
                registor:(0x00-0xff)
                value:(0x00-0xffff)

            Returns:
                bool: True | False, True for success, False for adc read failed
        """
        return self.adc_device.register_write(register,value)

        
    def adc_register_read(self,register):
        """ Read AD7175 adc register
        
            Args:
                registor:(0x00-0xff)
            
            Returns:
                value: register value
        """
        return self.adc_device.register_read(register)

    def adc_samplerate_set(self,channel,samplerate):
        """set  AD7175  measure channel samplerate

        Args:
            channel:("current","voltage") 
            samplerate:(value,"Hz") 

        Returns:
            bool: True | False, True for success, False for adc read failed

        Raise:
            KeyError,ValueError
        """
        if channel not in _datalogger_board_description["channel"]:
            raise ValueError(str("Input:")+str(channel), str("Args:")+str(_datalogger_board_description["channel"]))

        if not isinstance(samplerate,(tuple,list))  or len(samplerate) != 2:
            raise ValueError(str("Input:")+str(samplerate), str("Args:")+str(samplerate))

        if not self.adc_device.samplerate_set(_datalogger_board_description["channel"][channel]["adc_config"]["channel"],samplerate):
            return False

        self.adc_samplerate[channel]=samplerate

        return True

        
    def adc_samplerate_get(self,channel):
        """set  AD7175  measure channel samplerate

        Args:
            channel:("current","voltage")
            
        Returns:
            if success:
                tuple: (value,unit)
                    value samplerate,
                    unit is string type ('Hz')
            if fail:
                return False

        Raise:
            ValueError

        """
        if channel not in _datalogger_board_description["channel"]:
            raise ValueError(str("Input:")+str(channel), str("Args:")+str(_datalogger_board_description["channel"]))

        return self.adc_device.samplerate_get(_datalogger_board_description["channel"][channel]["adc_config"]["channel"])

    def board_initial(self):
        """ board initial
            
        ADC chip initial: samplerate,work mode,channel config
            
        Agrs:
            measure_path:{"channle":channel,"range":range}
                channel:["current","voltage"]
                range:
                    channel="current": range=("100uA","2mA") 
                    channel="voltage": range=("5V")
            
        Returns:
            bool: True | False, True for success, False for adc reset and initial failed.

        Raises: 
            KeyError,ValueError
        """
        
        logger.boot("%s board initial"%(self.profile["id"]))
        if not self.adc_device.single_sample_mode():
            logger.warning("%s board AD7175[%s]  chip single sample mode set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #ADC chip initial
        logger.boot("%s board AD7175[%s] chip initial"%(self.profile["id"], self.profile["adc"]["path"]))

        if not self.adc_device.reset():
            logger.warning("%s board AD7175[%s]  chip reset failed."%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        if not self.adc_device.is_comunication_ok():
            logger.warning("%s board AD7175[%s]  chip communication is not ok"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        if not self.adc_device.single_sample_mode():
            logger.warning("%s board AD7175[%s]  chip single sample mode set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #IFMODE register:  channel_flag, data bits, 
        if self.adc_device.ifmode_register_set("disable","24bits") is False:
            logger.warning("%s board AD7175[%s]  chip ifmode reg set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #Channel register: channel combination
        if self.adc_device.voltage_channel_disable("all") is False:
            logger.warning("%s board AD7175[%s]  chip channel reg  all disable config failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #setup register: code polar=bipolar,refrence=extern, buffer=enable
        if not self.adc_device.setup_register_set(_datalogger_board_description["channel"]["current"]["adc_config"]["channel"],
                                                                            "bipolar","extern","enable"):
            logger.warning("%s AD7175[%s]  chip current channel setup configure failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        if not self.adc_device.setup_register_set(_datalogger_board_description["channel"]["voltage"]["adc_config"]["channel"],
                                                                            "bipolar","extern","enable"):
            logger.warning("%s AD7175[%s]  chip voltage channel setup configure failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #filter register: samplerate config
        if not self.adc_device.samplerate_set(_datalogger_board_description["channel"]["current"]["adc_config"]["channel"],
                                                                        self.adc_samplerate["current"]):
            logger.warning("%s AD7175[%s]  chip current channel filter configure failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        if not self.adc_device.samplerate_set(_datalogger_board_description["channel"]["voltage"]["adc_config"]["channel"],
                                                                        self.adc_samplerate["voltage"]):
            logger.warning("%s AD7175[%s]  chip voltage channel filter configure failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #adc mode register: crystal clock
        if not self.adc_device.mode_register_set("crystal"):
            logger.warning("%s AD7175[%s]  mode register configure failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #the first one discarded
        if not self.adc_device.voltage_get(_datalogger_board_description["channel"]["current"]["adc_config"]["channel"],
                                            _datalogger_board_description["channel"]["current"]["adc_config"]["config"]):
            logger.warning("%s board AD7175[%s]  current  channel  first sample failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        if not self.adc_device.voltage_get(_datalogger_board_description["channel"]["voltage"]["adc_config"]["channel"],
                                            _datalogger_board_description["channel"]["voltage"]["adc_config"]["config"]):
            logger.warning("%s board AD7175[%s]  voltage  channel  first sample failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        if not self.adc_device.continue_mode_frame_config_set(self.chipnum,self.datalogger_samplerate[0]):
            logger.warning("%s AD7175[%s]  chipno and samplerate set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False
 
        #Channel register: channel combination
        if self.adc_device.voltage_channel_disable("all") is False:
            logger.warning("%s board AD7175[%s]  chip channel reg  all disable config failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False
             
        self.initial_flag = True
        
        return True

    def board_reset(self):
        """board reset
        Returns:
            bool: True | False, True for success, False for adc reset and initial failed.
        """

        if not self.datalogger_close():
            return False

        if not self.board_initial():
            return False
        
        return True

    def datalogger_open(self,channel="current"):
        """Datalogger work in continue sample mode

        Args:
            channel: ["voltage","current","all"]

        Returns:
            bool: True | False, True for success, False for adc reset and initial failed.

        Raise:
            ValueError
        """

#        self.adc_device.reset()
        self.framer.disable()
        self.framer.enable()
        self.framer.frame_state_set('always_open')
        self.framer.frame_config_set(0x01,1,4,'TS',config_list=[0,0,0,0,0,0,0,0,0,0])

        #IFMODE register:  channel_flag, data bits, 
        if self.adc_device.single_sample_mode() is False:
            logger.warning("%s board AD7175[%s]  chip single sample mode set failed"%(self.profile["id"], self.profile["id"], self.profile["adc"]["path"]))
            return False

        time.sleep(0.010)
        #IFMODE register:  channel_flag, data bits, 
        if self.adc_device.ifmode_register_set("disable","24bits") is False:
            logger.warning("%s board AD7175[%s]  chip ifmode reg set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #Channel register: channel combination
        if self.adc_device.voltage_channel_disable("all") is False:
            logger.warning("%s board AD7175[%s]  chip channel reg  all disable config failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False
        if self.adc_device.ifmode_register_set("enable","24bits") is False:
            logger.warning("%s board AD7175[%s]  chip ifmode reg set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False
        #Channel register: channel combination
        if self.adc_device.voltage_channel_disable("all") is False:
            logger.warning("%s board AD7175[%s]  chip channel reg  all disable config failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False
            #channel
        if not self.adc_device.voltage_channel_enable(_datalogger_board_description["channel"][channel]["adc_config"]["channel"],
                                                                                            _datalogger_board_description["channel"][channel]["adc_config"]["config"]):
            logger.warning("%s AD7175[%s]  chip %s channel configure failed"%(self.profile["id"], self.profile["adc"]["path"],channel))
            return False

        #samplerate
        if self.datalogger_samplerate_set(channel,self.datalogger_samplerate) is False:
            logger.warning("%s AD7175[%s]  chip datalogger samplerate configure failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        if not self.adc_device.continue_sample_mode():
             logger.warning("%s AD7175[%s]  chip datalogger continue mode config failed"%(self.profile["id"], self.profile["adc"]["path"]))
             return False

        return True

    def audio_upload(self, measure_time=100):
        """Datalogger work in continue sample mode

        Args:
            channel: ["voltage","current","all"]

        Returns:
            bool: True | False, True for success, False for adc reset and initial failed.

        Raise:
            ValueError
        """

        #IFMODE register:  channel_flag, data bits, 
        if self.adc_device.ifmode_register_set("enable","24bits") is False:
            logger.warning("%s board AD7175[%s]  chip ifmode reg set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #Channel register: channel combination
        if self.adc_device.voltage_channel_disable("all") is False:
            logger.warning("%s board AD7175[%s]  chip channel reg  all disable config failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False
        if not self.adc_device.voltage_channel_enable(_datalogger_board_description["channel"]['current']["adc_config"]["channel"],
                                                                                            _datalogger_board_description["channel"]['current']["adc_config"]["config"]):
            logger.warning("%s AD7175[%s]  chip %s channel configure failed"%(self.profile["id"], self.profile["adc"]["path"], "chan0"))
            return False
        #samplerate
        if self.datalogger_samplerate_set('current',self.datalogger_samplerate) is False:
            logger.warning("%s AD7175[%s]  chip datalogger samplerate configure failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        if not self.adc_device.continue_sample_mode():
             logger.warning("%s AD7175[%s]  chip datalogger continue mode config failed"%(self.profile["id"], self.profile["adc"]["path"]))
             return False
        time.sleep(float(measure_time)/1000)
        
        if self.adc_device.single_sample_mode() is False:
            logger.warning("%s board AD7175[%s]  chip single sample mode set failed"%(self.profile["id"], self.profile["id"], self.profile["adc"]["path"]))
            return False

        time.sleep(0.010)
        #IFMODE register:  channel_flag, data bits, 
        if self.adc_device.ifmode_register_set("disable","24bits") is False:
            logger.warning("%s board AD7175[%s]  chip ifmode reg set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #Channel register: channel combination
        if self.adc_device.voltage_channel_disable("all") is False:
            logger.warning("%s board AD7175[%s]  chip channel reg  all disable config failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        return True
    
    def datalogger_close(self,channel="all"):
        """Datalogger work in single sample mode

        Args:
            channel: ["all"]

        Returns:
            bool: True | False, True for success, False for adc reset and initial failed.

        Raise:
            ValueError
        """
        if channel != "all":
            raise ValueError("Input: "+str(channel),"Args: "+str(_datalogger_board_description["channel"].viewkeys()))

        if self.adc_device.single_sample_mode() is False:
            logger.warning("%s board AD7175[%s]  chip single sample mode set failed"%(self.profile["id"], self.profile["id"], self.profile["adc"]["path"]))
            return False
        self.framer.disable()
        time.sleep(0.010)
        #IFMODE register:  channel_flag, data bits, 
        if self.adc_device.ifmode_register_set("disable","24bits") is False:
            logger.warning("%s board AD7175[%s]  chip ifmode reg set failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        #Channel register: channel combination
        if self.adc_device.voltage_channel_disable("all") is False:
            logger.warning("%s board AD7175[%s]  chip channel reg  all disable config failed"%(self.profile["id"], self.profile["adc"]["path"]))
            return False

        return True

    def datalogger_samplerate_set(self,channel,samplerate):
        """Set Datalogger  samplerate

        Args:
            channel: ("voltage","current","all")
            samplerate:(value,unit)
                    value: samplerate 
                    unit: 'Hz'
        Note:
           For FPGA reasons, channel use all
        Returns:
            bool: True | False, True for success, False for adc read failed
        """
        if channel not in _datalogger_board_description["channel"] and channel != "all":
            raise ValueError(str("Input:")+str(channel), str("Args:")+str(_datalogger_board_description["channel"])+"all")

        if channel == "all":
            if not self.adc_samplerate_set("current",samplerate):
                return False
            if not self.adc_samplerate_set("voltage",samplerate):
                return False
        else:
            if not self.adc_samplerate_set(channel,samplerate):
                return False

            self.datalogger_samlerate= samplerate

        if not self.adc_device.continue_mode_frame_config_set(self.chipnum,samplerate[0]):
            return False
            
        return True


    def datalogger_measure(self,channel,count):
        """Get currrent  value from datalogger

        Args:
            channel:("voltage","current","all")
            count: 1- , int
                How much do you want to get data to participate in the calculation.

        Returns:
            if success:
                dict: {'sum":(value,unit),'sq':(value,unit),rms':(value,unit),'average':(value,unit),'max':(value,unit),'min':(value,unit)}
            if fail:
                return False
        """
        if channel not in _datalogger_board_description["channel"] and channel != "all":
            raise ValueError(str("Input:")+str(channel), str("Args:")+str(_datalogger_board_description["channel"])+"all")

        if count <= 0:
            count = 1

        result = self.adc_device.continue_mode_codes_get(count*2+20)
       
        if not result:
            return False
 
        if channel == "voltage":
            code_volt = [x for x in result if (x & 0x1) == 1]
            min_code_volt = min(code_volt)
            max_code_volt = max(code_volt)
            code_average =sum(code_volt)/len(code_volt)
            code_rms_voltage = math.sqrt(sum([x**2 for x in code_volt] )/len(code_volt))
            
            return {'rms':self.adc_device.code_2_mvolt(code_rms_voltage, self.vref, 24),
                    "average":self.adc_device.code_2_mvolt(code_average, self.vref, 24),
                    'max':self.adc_device.code_2_mvolt(max_code_volt, self.vref, 24),
                    'min': self.adc_device.code_2_mvolt(min_code_volt, self.vref, 24)}
            
        if channel == "current":
            code_current = [x for x in result if (x & 0x1) == 0]
            min_code_current = min(code_current)
            max_code_current = max(code_current)
            code_average =sum(code_current)/len(code_current)
            code_rms_current = math.sqrt(sum([x**2 for x in code_current] )/len(code_current))
            return {'rms':self.adc_device.code_2_mvolt(code_rms_current, self.vref, 24),
                    "average":self.adc_device.code_2_mvolt(code_average, self.vref, 24),
                    'max':self.adc_device.code_2_mvolt(max_code_current, self.vref, 24),
                    'min': self.adc_device.code_2_mvolt(min_code_current, self.vref, 24)}
            