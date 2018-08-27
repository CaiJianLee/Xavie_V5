#-*- utf-8 -*-
__version__ = 1.2
import sys,os
import re
sys.path.append("/opt/seeing/app")

from ee.overlay.i2cbus import *
from ee.bus.ci2c import CI2cBus
from ee.ipcore.axi4_iic import Axi4I2c


class I2cBus(object):
    def __init__(self, name, rate = 400000):
        self._name = name
        self._rate = rate
        if self._mount_on_fpga(name) is None:
            self._bus = CI2cBus(name)
        else:
            self._bus = Axi4I2c(name)
            self._bus.config(int(rate))

    def _mount_on_fpga(self, name):
        return re.search("AXI4_", name)	
		
    def write(self, dev_addr, data):
        return self._bus.write(dev_addr, data)
        
    def read(self, dev_addr, length):
        return self._bus.read(dev_addr, length)
        
    def rdwr(self, dev_addr, write_data, read_length):
        return self._bus.rdwr(dev_addr, write_data, read_length)
			
			
class I2cDetect(object):
    def __init__(self):
        pass
	
    def help(self):
        print('eg:i2cdetect <argv>')
        print("argv:")
        os.system('ls /dev/|grep i2c -i')

    def detect(self, dev_name):
        name  = dev_name
        i2cdev = I2cBus('/dev/'+name)
        print name
        #print i2cdev

        dev_list = ''
        dev_add = 0x00
        for dev_addr in range(0,0x80):
            rd = i2cdev.read(dev_addr,1)
            if rd != False:
                dev_list+='0x%02x  '%(dev_addr)
        return dev_list

#**************************************************************************#
	
print 'hello zynq.'
i2cdetect = I2cDetect()
if (len(sys.argv) == 1) or (sys.argv[1] in {"-h", "h", "help", "?"}):
    i2cdetect.help()
else:
    dev_name = sys.argv[1]
    dev_list = i2cdetect.detect(dev_name)
    print "device:"
    print dev_list
