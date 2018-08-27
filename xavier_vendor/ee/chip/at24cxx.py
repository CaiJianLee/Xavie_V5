"""A series of At24xx chip driver
    support list [at24c01,at24c02,at24c04,at24c08,at24c16,at24c32,at24c64,at24c128,at24c256,at24c512]
    write function neet some time to delay if dates been written in different memory page.
"""
import time
import copy
from ee.overlay.i2cbus import I2cBus
from ee.common import logger
from ee.profile.profile import Profile


at24cxx_list = {
    "at01":     {"page_size":8,         "page_num":16,      "memory_address_size":1, "mask":0x00, "wdelay":0.007},
    "at02":     {"page_size":8,         "page_num":32,      "memory_address_size":1, "mask":0x00, "wdelay":0.012},
    "at04":     {"page_size":16,        "page_num":32,      "memory_address_size":1, "mask":0x01, "wdelay":0.015},
    "at08":     {"page_size":16,        "page_num":64,      "memory_address_size":1, "mask":0x03, "wdelay":0.015},
    "at16":     {"page_size":16,        "page_num":128,     "memory_address_size":1, "mask":0x07, "wdelay":0.015},
    "at32":     {"page_size":32,        "page_num":128,     "memory_address_size":2, "mask":0x00, "wdelay":0.015},
    "at64":     {"page_size":32,        "page_num":256,     "memory_address_size":2, "mask":0x00, "wdelay":0.015},
    "at128":    {"page_size":64,        "page_num":256,     "memory_address_size":2, "mask":0x04, "wdelay":0.015},
    "at256":    {"page_size":64,        "page_num":512,     "memory_address_size":2, "mask":0x04, "wdelay":0.015},
    "at512":    {"page_size":128,       "page_num":512,     "memory_address_size":2, "mask":0x04, "wdelay":0.015},
}


class AT24Cxx(object):
    """A series of AT24xx chip driver

    Public methods:
    - read: read datas from eeprom
    - write: write datas to eeprom 
    """
    def __init__(self,at_profile,device_type):

        device_addr = at_profile["addr"]
        device_addr &=0x07
        device_addr |= 0x50
        self._device_addr = device_addr &(~at24cxx_list[device_type]["mask"])
        self._device_type = device_type
        
        try:
            switch_channel = at_profile["switch_channel"]
        except KeyError:
            switch_channel = None
        self.iic_bus = I2cBus(at_profile["bus"],switch_channel)

        self._page_size = at24cxx_list[device_type]["page_size"]
        self._chip_size = at24cxx_list[device_type]["page_num"] * at24cxx_list[device_type]["page_size"] 
        self._memory_address_size = at24cxx_list[device_type]["memory_address_size"]
        self._mask = at24cxx_list[device_type]["mask"]

    @staticmethod
    def parse_chip_profile(chip_profile, board_name):
        chip_id = chip_profile['id']
        eeprofile = Profile.get_eeprom()
        eeprofile[chip_id] = dict()

        for key, value in chip_profile.iteritems():
            eeprofile[chip_id][key] = copy.deepcopy(value)

        eeprofile[chip_id]['bus'] = Profile.get_bus_path(chip_profile['bus'])
        eeprofile[chip_id]['addr'] = int(chip_profile['addr'],16)

    def _memory_address_to_byte_list(self,memory_addr):
        """ Memory address change to byte list

            Args:
                memory_addr: (0x0000-0xffff)

            Returns:
                list type:
                  [high_byte,low_byte]
                  or [one_byte]
        """
        if self._memory_address_size == 2:
            return [(memory_addr >> 8 & 0xff),(memory_addr & 0xff)]
        else :
            return [(memory_addr & 0xff),]
        
    def read(self,memory_addr,length):
        """ Read datas from EEPROM

            Args:
                memory_addr: memory address
                  (0x0000-0xffff)
                length: How many data you want to read
                    int type

            Returns:
                False: read failed or too more data to read
                or
                list type: read data
                [data1,data2,...,datan]
        """

        if memory_addr + length > self._chip_size :
            logger.warn ("no more then  %s to read",str(self._chip_size))
            return False

        read_len = length
        read_addr = memory_addr
        read_bytes = 0
        if  ((read_addr & (self._page_size - 1)) +read_len) > self._page_size :
            read_bytes = self._page_size - (read_addr & (self._page_size - 1))
        else :
            read_bytes = read_len

        result = []
        while read_len > 0:
            #device address mix
            if self._device_type == "at04" or self._device_type == "at08" or self._device_type == "at16" :
                device_addr = self._device_addr| ((read_addr >> 8) & self._mask)
            else:
                device_addr = self._device_addr

            #memory address to list data type
            mem_addr = self._memory_address_to_byte_list(read_addr)

            #FPGA i2c bus a frame max size is 32 bytes data.
            if read_bytes > (32-1-len(mem_addr)):
               read_bytes =  32-1-len(mem_addr)

            read_result= self.iic_bus.rdwr(device_addr,mem_addr,read_bytes)
            if not read_result:
                return False
                
            result += read_result
            read_len -= read_bytes
            read_addr += read_bytes
            if read_len > self._page_size:
                read_bytes = self._page_size
            else :
                read_bytes = read_len

        return result
    
    def write(self,memory_addr,data):
        """ Write datas to EEPROM

            Args:
                memory_addr: memory address
                  (0x0000-0xffff)
                data: list type
                [data1,...,data_n]

            Returns:
                bool: True | False, True for success, False for failed or to more data to write.
        """
        write_len = len(data)
        if memory_addr + write_len > self._chip_size :
            logger.warn ("no more then %s to write ",str(self._chip_size))
            return False

        data = list(data)
        write_addr = memory_addr
        write_bytes = 0
        logger.debug("at24cxx write " + str(write_addr) + ' len ' + str(write_len))
        if write_len > self._page_size or (write_addr & (self._page_size - 1)) != 0:
            write_bytes = self._page_size - (write_addr & (self._page_size - 1))
        else :
            write_bytes = write_len


        while write_len > 0:
            if self._device_type == "at04" or self._device_type == "at08" or self._device_type == "at16" :
                device_addr = self._device_addr| ((write_addr >> 8) & self._mask)
            else:
                device_addr = self._device_addr
                
            mem_addr = self._memory_address_to_byte_list(write_addr)
            #FPGA i2c bus a frame max size is 32 bytes data.
            if write_bytes > (32-1-len(mem_addr)):
               write_bytes =  32-1-len(mem_addr)

            write_data = data[0:write_bytes]

            ret = self.iic_bus.write(device_addr,mem_addr+write_data)
            if not ret:
                return False

            del data[0:write_bytes]
            write_len -= write_bytes
            write_addr += write_bytes
            if write_len > self._page_size:
                write_bytes = self._page_size
            else :
                write_bytes = write_len
            time.sleep(at24cxx_list[self._device_type]["wdelay"])

        return True
