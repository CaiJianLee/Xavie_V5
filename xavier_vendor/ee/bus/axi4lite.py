import struct
import os
import ctypes

import ee.common.utility as utility
from ee.common.ddp_client import DDPClient 
from ee.common import logger

libname = utility.get_lib_path() + "/libsgfpga.so"
if libname and os.path.isfile(libname):
    libaxi4lite = ctypes.cdll.LoadLibrary(libname) 
else:
    libaxi4lite = None

class Axi4lite(object):
    def __init__(self, name, register_num): 
        self._name = name
        self._register_num = register_num
        self._axi4lite = None
        
    def open(self):
        logger.debug('libsgfpaga path is %s'%(libname))
        if libaxi4lite is None:
            self._axi4lite = RPCAxi4lite(self._name, self._register_num)
        else:
            self._axi4lite = CAxi4lite(self._name, self._register_num)
        
        return self._axi4lite.open()
            
    
    def read(self, addr, length):
        """ read list data from axi4lite bus
            Args:
                addr(int)   : the starting read address
                length(int)   : the number of read data bytes
            Returns:
                on success, return a list
                on error, return False
        """
        return self._axi4lite.read(addr, length)

    def write(self, addr, data, length):
        """ write list data to axi4lite bus
            Args:
                addr(int)   : the starting write address
                data(list)   : a int list
                length(int)   : the number of write data bytes
            Returns:
                on success, return True
                on error, return False
        """
        return self._axi4lite.write(addr, data, length)
    
    def read_array(self, addr, length, bitwide):
        """ read list data from axi4lite bus fixed address
            Args:
                addr(int)   : the fixed read address
                length(int)   : the number of read data bytes
                bitwide(int)  : the number of data bitwide,8/16/32
            Returns:
                on success, return a list
                on error, return False
        """
        return self._axi4lite.read_array(addr, length, bitwide)

    def write_array(self, addr, data, length, bitwide):
        """ write list data to axi4lite bus fixed address
            Args:
                addr(int)   : the fixed write address
                data(list)   : a int list
                length(int)   : the number of write data bytes
                bitwide(int)  : the number of data bitwide,8/16/32
            Returns:
                on success, return True
                on error, return False
        """
        return self._axi4lite.write_array(addr, data, length, bitwide)
    
    def read_byte(self, addr, length):
        """ read byte stream data from axi4lite bus
            Args:
                addr(int)   : the starting read address
                length(int)   : the number of read data bytes
            Returns:
                on success, return a string of byte stream data
                on error, return False
        """
        return self._axi4lite.read_byte(addr, length)

    def write_byte(self, addr, data, length):
        """ write byte stream data to axi4lite bus
            Args:
                addr(int)   : the starting write address
                data(string)   : a string of byte stream data
                length(int)   : the number of write data bytes
            Returns:
                on success, return True
                on error, return False
        """
        return self._axi4lite.write_byte(addr, data, length)

    def read_byte_array(self, addr, length, bitwide):
        """ read byte stream data from axi4lite bus fixed address
            Args:
                addr(int)   : the fixed read address
                length(int)   : the number of read data bytes
                bitwide(int)  : the number of data bitwide,8/16/32
            Returns:
                on success, return a string of byte stream data
                on error, return False
        """
        return self._axi4lite.read_byte_array(addr, length, bitwide)

    def write_byte_array(self, addr, data, length, bitwide):
        """ write byte stream data to axi4lite bus fixed address
            Args:
                addr(int)   : the fixed write address
                data(string)   : a string of byte stream data
                length(int)   : the number of write data bytes
                bitwide(int)  : the number of data bitwide,8/16/32
            Returns:
                on success, return True
                on error, return False
        """
        return self._axi4lite.write_byte_array(addr, data, length, bitwide)

class CAxi4lite(object):
    def __init__(self, name, register_num):
        self._name = name
        self._register_num = register_num
        self._libaxi4lite = libaxi4lite 
        self._base_addr = 0

    def __del__(self):
        if self._base_addr != 0:
            self._close()

        self._base_addr = 0
        
    def open(self):
        read_data = ctypes.c_uint()
        logger.info('open fpga device %s register number %d'%(self._name, self._register_num))
        status = self._libaxi4lite.sg_fpga_open(self._name, self._register_num, ctypes.byref(read_data))
        if (status < 0):
            logger.warning('open %s fail,return value is %d'%(self._name,status))
            return False

        # TODO return address directly
        addr = read_data.value
        logger.info("\"%s\" map addr is %#x"%(self._name, addr))
        if addr == 0:
            return False
        else:
            self._base_addr = addr
            return True
    
    def _close(self):
        logger.info("close fpga device %s " %(self._name))
        if self._base_addr != 0:
            self._libaxi4lite.sg_fpga_close(self._base_addr, self._register_num)
    
    def read(self, addr, length):
        if self._base_addr == 0:
            logger.error("fpga device:%s not opened" %(self._name))
            return False

        read_data = (ctypes.c_char * length)()
        status = self._libaxi4lite.sg_fpga_read(self._base_addr + addr, read_data, length)
        
        if (status < 0):
            logger.info("read fpga device:%s  addr:0x%x length:%s fail" %(self._name, addr, length))
            return False

        data = list(struct.unpack('%dB'%length,read_data.raw))
        logger.debug("read fpga device:%s  addr:0x%x length:%s data : %s " 
                        %(self._name, addr, length, logger.print_list2hex(data)))
        return data
    
    def write(self, addr, data, length):
        if self._base_addr == 0:
            logger.error("fpga device:%s not opened" %(self._name))
            return False

        logger.debug("write fpga device:%s  addr:0x%x length:%d data: %s"
                    %(self._name, addr, length, logger.print_list2hex(data)))
        write_data = (ctypes.c_ubyte * length)(*data)
        status = self._libaxi4lite.sg_fpga_write(self._base_addr + addr, write_data, length)
        
        if(status < 0):
            logger.warning("write fpga device:%s  addr:0x%x length:%d data: %s fail"
                        %(self._name, addr, length, logger.print_list2hex(data)))
            return False
    
        return True
    
    def read_array(self, addr, length, bitwide):
        if self._base_addr == 0:
            logger.error("fpga device:%s not opened" %(self._name))
            return False

        read_data = (ctypes.c_char * length)()
        status = self._libaxi4lite.sg_fpga_read_array(self._base_addr + addr, read_data, length, bitwide)
        
        if (status < 0):
            logger.warning("read fpga device %s array addr: 0x%x length:%d fail" 
                        %(self._name, addr, length))
            return False
        
        data = list(struct.unpack('%dB'%length,read_data.raw))
        logger.debug("read fpga device %s array addr:0x%x  length:%d data:%s" 
                    %(self._name, addr, length, logger.print_list2hex(data)))
        return data
    
    def write_array(self, addr, data, length, bitwide):
        if self._base_addr == 0:
            logger.error("fpga device:%s not opened"%(self._name))
            return False

        logger.debug("write fpga device %s array addr: 0x%x length:%d data:%s" 
                    %(self._name, addr, length, logger.print_list2hex(data)))
        write_data = (ctypes.c_ubyte * length)(*data)
        status = self._libaxi4lite.sg_fpga_write_array(self._base_addr + addr, write_data, length, bitwide)
        
        if(status < 0):
            logger.warning("write fpga device %s array addr: 0x%x length:%d data:%s fail" 
                        %(self._name, addr, length, logger.print_list2hex(data)))
            return False
    
        return True

    def read_byte(self, addr, length):
        if self._base_addr == 0:
            logger.error("fpga device:%s not opened" %(self._name))
            return False

        read_data = (ctypes.c_char * length)()
        status = self._libaxi4lite.sg_fpga_read(self._base_addr + addr, read_data, length)
        
        if (status < 0):
            logger.info("read fpga device:%s  addr:0x%x length:%s fail" %(self._name, addr, length))
            return False

        data = read_data.raw
        #logger.debug("read fpga device:%s  addr:0x%x length:%s data : %s " 
                        #%(self._name, addr, length, logger.print_list2hex(data)))
        return data

    def write_byte(self, addr, data, length):
        if self._base_addr == 0:
            logger.error("fpga device:%s not opened" %(self._name))
            return False
            
        status = self._libaxi4lite.sg_fpga_write(self._base_addr + addr, ctypes.c_char_p(data), length)
        
        if(status < 0):
            logger.warning("write fpga device:%s  addr:0x%x length:%d fail"
                        %(self._name, addr, length))
            return False
    
        return True

    def read_byte_array(self, addr, length, bitwide):
        if self._base_addr == 0:
            logger.error("fpga device:%s not opened" %(self._name))
            return False

        read_data = (ctypes.c_char * length)()
        #status = self._libaxi4lite.sg_fpga_read_array(self._base_addr + addr, read_data, length)
        status = self._libaxi4lite.sg_fpga_read_array(self._base_addr + addr, read_data, length, bitwide)
        if (status < 0):
            logger.warning("read fpga device %s array addr: 0x%x length:%d fail" 
                        %(self._name, addr, length))
            return False
        
        data = read_data.raw
        return data

    def write_byte_array(self, addr, data, length, bitwide):
        if self._base_addr == 0:
            logger.error("fpga device:%s not opened"%(self._name))
            return False
        #status = self._libaxi4lite.sg_fpga_write_array(self._base_addr + addr, ctypes.c_char_p(data), length)
        status = self._libaxi4lite.sg_fpga_write_array(self._base_addr + addr, ctypes.c_char_p(data), length, bitwide)
        
        if(status < 0):
            logger.warning("write fpga device %s array addr: 0x%x length:%d fail" 
                        %(self._name, addr, length))
            return False
    
        return True

class FpgaIOError(Exception):
    pass

class RPCAxi4lite(object):
    def __init__(self, name, register_num):
        self.__devid = None
        self.__name = name
        self.__register_num = register_num
        
    def __del__(self):
        if self.__devid is not None:
            self.__close()
            
        self.__ddp.stop()
        
    def open(self):
        self.__ddp = DDPClient(os.environ.get('ARM_BOARD_IP'), 22730)
        self.__ddp.start()
        msg = self.__ddp.call('fpga_open', [self.__name, self.__register_num])
        if 'error' in msg.keys():
            logger.error("fpga devie %s open fail, the error:%r" %(self.__name, msg['error']))
            self.__ddp.stop()
            return False
        elif 'result' not in msg.keys():
            logger.error("fpga devie %s open fail" %(self.__name))
            self.__ddp.stop()
            return False
        else:
            self.__devid = msg['result']
            return True
        
    def read(self, addr, length):
        msg = self.__ddp.call('fpga_read', [self.__devid, addr, length])
        if 'error' in msg.keys():
            logger.error('fpga read device:%s addr:0x%x length:%d error:%s', self.__name, addr, length, msg['error'])
            raise FpgaIOError('read register failed')
        elif 'result' not in msg.keys():
            raise FpgaIOError('read register failed')
        else:
            return msg['result']

    def write(self, addr, data, length):
        msg = self.__ddp.call('fpga_write', [self.__devid, addr, length, data])
        if 'error' in msg.keys():
            logger.error('fpga write device:%s addr:0x%x length: %d error:%s',self.__name,  addr, length, msg['error'])
            return False
        elif 'result' not in msg.keys():
            return False
        else:
            return True
        
    def read_array(self, addr, length):
        msg = self.__ddp.call('fpga_read_array', [self.__devid, addr, length])
        if 'error' in msg.keys():
            logger.error('fpga read device:%s addr:0x%x length:%d error:%s', self.__name, addr, length, msg['error'])
            raise FpgaIOError('read register failed')
        elif 'result' not in msg.keys():
            raise FpgaIOError('read register failed')
        else:
            return msg['result']
            
    def write_array(self, addr, data, length):
        msg = self.__ddp.call('fpga_write_array', [self.__devid, addr, length, data])
        if 'error' in msg.keys():
            logger.error('fpga write device:%s addr:0x%x length: %d error:%s',self.__name,  addr, length, msg['error'])
            return False
        elif 'result' not in msg.keys():
            return False
        else:
            return True
    
    def __close(self):
        msg = self.__ddp.call('fpga_close', [self.__devid])
        if 'error' in msg.keys():
            logger.error('fpga close '+str(self._name)+ ' error: '+str( msg['error']))
            return False
        elif 'result' not in msg.keys():
            return False
        else:
            return True
    

    
