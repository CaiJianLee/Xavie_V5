import os
import struct
import ctypes
from ee.common import logger
import ee.common.utility as utility

libname = utility.get_lib_path() + "/libsgi2c.so"
if libname and os.path.isfile(libname):
    libi2c = ctypes.cdll.LoadLibrary(libname) 
else:
    libi2c = None

class CI2cBus(object):
    def __init__(self,name):
        self._name = name
        self._fileno = 0
        self._bus = libi2c 

    def __open(self):
        logger.debug("open i2c device %s" %(self._name))
        self._fd = self._bus.sg_i2c_open(self._name)
        if self._fd <= 0:
            logger.error("open i2c device %s fail" %(self._name))
            return False
        else:
            return True
    
    def read(self,  dev_addr,  length):
        logger.debug("read i2c device %s addr:0x%x length:%d" %(self._name, dev_addr, length))
        if not self.__open():
            return False

        # TODO performance
        read_data = (ctypes.c_char * length)()
        status = self._bus.sg_i2c_read(self._fd, dev_addr, read_data, length)
        self.__close()
        if (status < 0):
            logger.warning("read i2c device %s addr:0x%x length:%d fail" %(self._name, dev_addr, length))
            return False

        data = []
        for i in range(length):
            data.append(ord(read_data[i]) & 0xff)

        return data

    def write(self, dev_addr, data):
        logger.debug("write i2c device %s addr:0x%x length:%d data:%s" 
                    %(self._name, dev_addr, len(data), logger.print_list2hex(data)))
        if not self.__open():
            return False
        
        length = len(data)
        write_data = (ctypes.c_ubyte * length)(*data)
        status = self._bus.sg_i2c_write(self._fd, dev_addr, write_data, length)
        self.__close()
        
        if(status < 0):
            logger.warning("write i2c device %s addr:0x%x length:%d data:%s fail" 
                        %(self._name, dev_addr, len(data), logger.print_list2hex(data)))
            return False

        return True
    
    '''write_data is a data list , read_lenght ,the size of your will read''' 
    def rdwr(self, dev_addr, write_data_list,read_length):
        logger.debug("rdwr i2c device %s addr:0x%x  write length:%d data:%s read length:%d" 
                    %(self._name, dev_addr, len(write_data_list), logger.print_list2hex(write_data_list), read_length))
            
        if not self.__open():
            return False
        
        write_length = len(write_data_list)
        write_data = (ctypes.c_ubyte * write_length)(*write_data_list)
        read_data = (ctypes.c_char * read_length)()
        status = self._bus.sg_i2c_rdwr(self._fd, dev_addr,write_data,write_length,read_data,read_length)
        self.__close()

        if(status < 0):
            logger.warning("rdwr i2c device %s addr:0x%x  write length:%d data:%s read length:%d fail" 
                        %(self._name, dev_addr, len(write_data_list), logger.print_list2hex(write_data_list), read_length))
            return False
        
        data = list(struct.unpack('%dB'%read_length, read_data.raw))
        return data
    
    def __close(self):
        logger.debug("close i2c device %s" %(self._name))
        self._bus.sg_i2c_close(self._fd)
        return True