
from ee.overlay.i2cbus import I2cBus
from ee.common import logger
from collections import OrderedDict
from ee.profile.profile import Profile

cat9555_registers={
    "input_port_0":0x00,
    "input_port_1":0x01,
    "output_port_0":0x02,
    "output_port_1":0x03,
    "inversion_port_0":0x04,
    "inversion_port_1":0x05,
    "dir_configuration_port_0":0x06,
    "dir_configuration_port_1":0x07,
}


class CAT9555(object):
    def __init__(self,cat_profile):
        device_addr = cat_profile["addr"]
        device_addr &= 0x07
        self._device_addr = device_addr|0x20
        try:
            switch_channel = cat_profile["switch_channel"]
        except KeyError:
            switch_channel = None
        self.iic_bus = I2cBus(cat_profile["bus"],switch_channel)

    @staticmethod
    def parse_chip_profile(chip_profile, board_name):
        chipname = chip_profile['id']

        extendios = Profile.get_extendio()
        extendios[board_name] = extendios.setdefault(board_name, OrderedDict())
        extendio = extendios[board_name]

        extendio[chipname] = dict()
        extendio[chipname]['bus'] = Profile.get_bus_path(chip_profile['bus'])
        extendio[chipname]['addr'] = int(chip_profile['addr'],16)
        extendio[chipname]['partno'] = chip_profile['partno']
        extendio[chipname]['switch_channel'] = chip_profile['switch_channel']

        chips = Profile.get_chips()
        chips[chipname] = extendio[chipname]

        bit_values = 0
        bit_dir = 0
        dir_value = {'input': 1,'output': 0}
        for pin in chip_profile['property']:
            pinname = pin['id']

            extendio[pinname] = dict()
            extendio[pinname]['pin'] = pin['pin']
            extendio[pinname]['chip'] = chipname

            if 'default' in pin.keys():
                bit_values |= (int(pin['default']) << (int(pin['pin']) - 1))
            if 'dir' in pin.keys():
                bit_dir |= (dir_value[pin['dir']] << (int(pin['pin']) - 1))

        value_list = []
        dir_list = []
        for x in xrange(len(chip_profile['property'])/8):
            value_list.append((bit_values >> (x*8)) & 0xff)
            dir_list.append((bit_dir >> (x*8)) & 0xff)

        initconfig = Profile.get_initconfig()
        initconfig['extendio'] = initconfig.setdefault('extendio', OrderedDict())
        initconfig['extendio'][board_name] = initconfig['extendio'].setdefault(board_name,OrderedDict())
        initconfig['extendio'][board_name][chipname] = dict(dir=dir_list, value=value_list)

    def read(self,register_addr,read_length):
        """Read data from register

            Returns:
                list type: [data0,data1,...,data_n]
                   data_n (0x00-0xff)
        """
        data=[]
        data.append(register_addr)
        logger.debug("cat9555 device read addr:"+hex(register_addr)+" len:"+str(read_length))
        result = self.iic_bus.rdwr(self._device_addr,data,read_length)
        return result

    def write(self,register_addr,data_list):
        """ Write data to  register

            Args:
                register_addr:  int
                    0x00-0x07
                data_list :[data0,data1,...,datan]
                    data_n (0x00-0xff)

            Returns:
                bool: True | False, True for success, False for adc read failed
        """
        logger.debug("cat9555 device write addr :"+hex(register_addr)+" data:"+logger.print_list2hex(data_list))
        write_data = []
        write_data.append(register_addr)
        write_data += data_list[0:2]
        result = self.iic_bus.write(self._device_addr,write_data)
        return result

    def write_dir_config(self,dir_config_list):
        """ Write data to dir config register

            Args:
                dir_config_list:[port0, port1]
                    port0,port1: (0x00-0xff)
                        0: Output,1:Input
            Returns:
                bool: True | False, True for success, False for adc read failed
        """
        return self.write(cat9555_registers["dir_configuration_port_0"],dir_config_list)


    def read_dir_config(self):
        """ Read dir config from register

            Returns:
                list type: [port0,port1]
                    port0,port1: (0x00-0xff)
                        0: Output,1:Input
        """
        return self.read(cat9555_registers["dir_configuration_port_0"],2)

    def read_inport(self):
        """ Read input state from register

            Returns:
                list type: [port0,port1]
                    port0,port1: (0x00-0xff)
                        0: Low level,1:High level
        """
        return self.read(cat9555_registers["input_port_0"],2)


    ''' status is a list , status[0] write to port_0. status[1] write to port_1. '''
    def write_outport(self,data_list):
        """ Write data to output potr register

            Args:
                data_list:[port0, port1]
                    port0,port1: (0x00-0xff)
                        0: Low level,1:High level
            Returns:
                bool: True | False, True for success, False for adc read failed
        """
        return self.write(cat9555_registers["output_port_0"],data_list)

    ''' return result is a list , result[0] from  port_0. result[1] from port_1. '''
    def read_outport(self):
        """ Read output set state from register

            Returns:
                list type: [port0,port1]
                    port0,port1: (0x00-0xff)
                        0: Low level,1:High level
        """
        return self.read(cat9555_registers["output_port_0"],2)



    def write_inversion(self,data_list):
        """ Write data to polarity inversion port register

            Args:
                data_list:[port0, port1]
                    port0,port1: (0x00-0xff)
                        0: normal, 1: inversion
            Returns:
                bool: True | False, True for success, False for adc read failed
        """
        return self.write(cat9555_registers["inversion_port_0"],data_list)


    def read_inversion(self):
        """ Read polarity inversion config from register

            Returns:
                list type: [port0,port1]
                    port0,port1: (0x00-0xff)
                        0: normal, 1: inversion
        """
        return self.read(cat9555_registers["inversion_port_0"],2)


    def read_out_in_state(self):
        """Read IO state from output or input register
            if IO dir config Output read output, also input read input

            Returns:
                list type: [port0,port1]
                    port0,port1: (0x00-0xff)
                        0: Low level,1:High level
        """

        return self.read_inport()



