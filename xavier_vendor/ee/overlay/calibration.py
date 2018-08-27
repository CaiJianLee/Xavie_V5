import struct
import ee.overlay.eeprom as Eeprom
from ee.common import logger


''' for using ,as follow: 
#-*- coding: UTF-8 -*-

audio_cal_profile={
    "unit_size":9,      #cal parameter size {gain,offset,flag}, filled with 9, 10, 12 or 17
    "base_addr":0x80,   #eeprom calibration data store start address
    "max_addr":0x3ff,   #eeprom calibration dta store end address

    "range":{
        "AUDIO_VPP":[# (,1000),[1000, 3000), [3000, 5000),[5000,)
            {"level":1,"limit":(1000,"mV"),"addr_offset":0},    # 'addr_offset': the offset of unit in eeprom,
            {"level":2,"limit":(3000,"mV"),"addr_offset":1},    # 'level': is mapped to addr_offset
            {"level":3,"limit":(5500,"mV"),"addr_offset":2},    # 'limit':(value, flag), the flag just for sign
        ],
        "AUDIO_RMS":[
            {"level":1,"limit":(1000,"mV"),"addr_offset":3},  
            {"level":2,"limit":(3000,"mV"),"addr_offset":4},
            {"level":3,"limit":(5500,"mV"),"addr_offset":5},
        ],
        "AUDIO_OUTPUT":[
            {"level":1,"limit":(1000,"Hz"),"addr_offset":6},  
            {"level":2,"limit":(3000,"Hz"),"addr_offset":7},
            {"level":3,"limit":(5500,"Hz"),"addr_offset":8},
        ],
        }
    }
eeprom_profile = {"partno": "AT24C08", "id":"audio","bus": "I2C_CODEC", "switch_channel": "none","addr": "0x50"}


gain = 2
offset = 1
level = 3

Cal = CALIBRATION(audio_cal_profile, eeprom_profile)
Cal.write('AUDIO_VPP', level,gain, offset)
Cal.read('AUDIO_VPP',level)                 # (2, 1)
Cal.calibrate('AUDIO_VPP', [3000, 4000])    # [6001, 8001]

'''

class CALIBRATION(object):
    def __init__(self, cal_profile, eeprom_profile):
        self.cal_profile = cal_profile
        self.eeprom_profile = eeprom_profile
        
        ''' select the 3 base function for size of unit'''
        unit_size = cal_profile['unit_size']
        self.calibration_read = eval("calibration_float%s_read"%unit_size)
        self.calibration_write= eval("calibration_float%s_write"%unit_size)
        self.calibration_pipe = calibration_pipe

    def _get_eeprom_addr(self, range_name, level):
        if range_name not in self.cal_profile["range"]:
            raise ValueError("Input: "+range_name,"Args: "+str(self.cal_profile["range"].viewkeys()))
        
        range_list = self.cal_profile["range"][range_name]
        wrong_level_flag = 1
        
        for range_dict in range_list:
            if range_dict["level"] == level:
                addr_offset = range_dict["addr_offset"]
                wrong_level_flag = 0
                break
            
        if wrong_level_flag == 1:
            raise ValueError("Input: "+str(level) + "out of range")
        
        base_addr = self.cal_profile["base_addr"]
        max_addr = self.cal_profile["max_addr"]
        unit_size = self.cal_profile["unit_size"]
        address = base_addr + addr_offset * unit_size
        if address > max_addr:
            logger.error("eeprom chip addr out of range")
            return False

        return address

    def write(self,range_name, level, gain, offset):
        address = self._get_eeprom_addr(range_name,level)
        if address == False:
            return False
        
        eeprom_profile = self.eeprom_profile
        if not self.calibration_write(eeprom_profile,address,gain,offset):
            logger.error("calibration write fail")
            return False
        
        return True

    def read(self, range_name, level):
        address = self._get_eeprom_addr(range_name,level)
        if address == False:
            return False
        
        eeprom_profile = self.eeprom_profile
        calibration_value = self.calibration_read(eeprom_profile,address)
        if calibration_value == False:
            logger.error("calibration read fail")
            return False
        
        return calibration_value

    def calibrate(self, range_name, original_value_list):
        if range_name not in self.cal_profile["range"]:
            raise ValueError("Input: "+range_name,"Args: "+str(self.cal_profile["range"].viewkeys()))
        
        range_list = self.cal_profile["range"][range_name]
        return_value_list = []
        
        for original_value in original_value_list:
            over_limit_flag = 1
            for range_dict in range_list:
                limit = range_dict["limit"][0]
                if original_value < limit:
                    level = range_dict["level"]
                    over_limit_flag = 0
                    break
                
            if over_limit_flag == 1:
                level = range_list[-1]["level"]
                
            calibration_value = self.read(range_name,level)
            if calibration_value == False:
                return False
            
            return_value_list.append(self.calibration_pipe(original_value,calibration_value[0],calibration_value[1]))
            
        return return_value_list




cal_double_unit_size = 17
cal_float_unit_size = 9
cal_float12_unit_size=12 


def calibration_float9_write(ee_profile,address,gain,offset):
    return calibration_float_write(ee_profile,address,gain,offset)

def calibration_float9_read(ee_profile,address):
    return calibration_float_read(ee_profile,address)

def calibration_float17_write(ee_profile,address,gain,offset):
    return calibration_double_write(ee_profile,address,gain,offset)

def calibration_float17_read(ee_profile,address):
    return calibration_double_read(ee_profile,address)


def calibration_pipe(original_value,gain,offset):
    """Get the calibration results 

        Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address
            gain:   float data
            offset: float data

        Returns:
            bool: True | False, True for success, False for adc read failed
    """
    cal_value = original_value*gain+offset
    return cal_value


def calibration_float_read(ee_profile,address):
    """Calibration data read  
       {float gain,float offset,uint8_t flag}

        Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address

        Returns:
            (gain,offset)
                 float data
    """
    data = Eeprom.read(ee_profile,address,9)
    if data is False:
        return False

    s = struct.Struct("9B")
    pack_data= s.pack(*data)
    
    s = struct.Struct("2fB")
    result = s.unpack(pack_data)

    flag = result[2]
    if 0x5a != flag:
        return (1.0,0.0)
    else:
        return (result[0],result[1])


def calibration_float_write(ee_profile,address,gain,offset):
    """Calibration data write  
       {float gain,float offset,uint8_t flag}

        Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address
            gain:   float data
            offset: float data

        Returns:
            bool: True | False, True for success, False for adc read failed
    """
    data=(gain,offset,0x5a)
    s = struct.Struct("2fB")
    pack_data= s.pack(*data)
    
    s = struct.Struct("9B")
    data =  s.unpack(pack_data)
    result = Eeprom.write(ee_profile,address,data)

    return result

def calibration_double_read(ee_profile,address):
    """Calibration data read  
       {double gain,double offset,uint8_t flag}

        Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address

        Returns:
            (gain,offset)
                 double data
    """
    data = Eeprom.read(ee_profile,address,12)
    if data is False:
        return False

    s = struct.Struct("17B")
    pack_data= s.pack(*data)
    
    s = struct.Struct("2dB")
    result = s.unpack(pack_data)

    flag = result[2]
    if 0x5a != flag:
        return (1.0,0.0)
    else:
        return (result[0],result[1])


def calibration_double_write(ee_profile,address,gain,offset):
    """ Calibration data write  
         {double gain,double offset,uint8_t flag}

         Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address
            gain: doble data
            offset: double data

        Returns:
            bool: True | False, True for success, False for adc read failed
    """
    data=(gain,offset,0x5a)
    s = struct.Struct("2dB")
    pack_data= s.pack(*data)
    
    s = struct.Struct("17B")
    data =  s.unpack(pack_data)
    result = Eeprom.write(ee_profile,address,data)

    return result


def calibration_float12_read(ee_profile,address):
    """Calibration data read.
        Compatible with the old case.
        {float gain,float offset,uint8_t flag,uint8_t dummy,uint8_t dummy,uint8_t dummy}
       
        Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address

        Returns:
            (gain,offset)
                 float data
    """
    data = Eeprom.read(ee_profile,address,12)
    if data is False:
        return False

    s = struct.Struct("12B")
    pack_data= s.pack(*data)
    
    s = struct.Struct("2f4B")
    result = s.unpack(pack_data)

    flag = result[2]
    if 0x5a != flag:
        return (1.0,0.0)
    else:
        return (result[0],result[1])


def calibration_float12_write(ee_profile,address,gain,offset):
    """ Calibration data write 
         Compatible with the old case.
         {float gain,float offset,uint8_t flag,uint8_t dummy,uint8_t dummy,uint8_t dummy}

         Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address
            gain:   float data
            offset: float data

         Returns:
            bool: True | False, True for success, False for adc read failed
    """
    data=(gain,offset,0x5a,0xff,0xff,0xff)
    s = struct.Struct("2f4B")
    pack_data= s.pack(*data)
    
    s = struct.Struct("12B")
    data =  s.unpack(pack_data)
    result = Eeprom.write(ee_profile,address,data)

    return result

def calibration_float10_read(ee_profile,address):
    """Calibration data read.
        Compatible with the old case.
        {float gain,float offset,uint8_t flag,uint8_t dummy,uint8_t dummy,uint8_t dummy}
       
        Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address

        Returns:
            (gain,offset)
                 float data
    """
    data = Eeprom.read(ee_profile,address,10)
    if data is False:
        return False

    s = struct.Struct("10B")
    pack_data= s.pack(*data)
    
    s = struct.Struct("10B")
    result = s.unpack(pack_data)
    checksum_read = result[8] | result[9] << 8

    checksum = 0x00
    for i in range(len(result) - 2):
        checksum += result[i]
    if checksum != checksum_read or checksum == 0:
        return (1.0,0.0)
    else:
        s = struct.Struct("2f2B")
        result = s.unpack(pack_data)
        return (result[0],result[1])


def calibration_float10_write(ee_profile,address,gain,offset):
    """ Calibration data write 
         Compatible with the old case.
         {float gain,float offset,uint8_t flag,uint8_t dummy,uint8_t dummy,uint8_t dummy}

         Args:
            ee_profile: dict type, the eeprom profile which calibration data stored
            address: the starting address
            gain:   float data
            offset: float data

         Returns:
            bool: True | False, True for success, False for adc read failed
    """
    data=(gain,offset)
    s = struct.Struct("2f")
    pack_data= s.pack(*data)
    
    s = struct.Struct("8B")
    data =  s.unpack(pack_data)
    checksum = 0x00
    for i in range(len(data)):
        checksum += data[i]
    data_byte = list(data)
    data_byte.append(checksum & 0xff)
    data_byte.append((checksum >> 8) & 0xff)
    result = Eeprom.write(ee_profile,address,data_byte)

    return result