__author__='Mingcheng'

from collections import OrderedDict
from ee.eedispatcher import EEDispatcher

class Profile():

    _base_board_name=None
    '''
    example of _exendio
    {
        "base_board_id":{
            "cp1": {"partno": "CAT9555", "bus": "/dev/i2c-0", "addr": 0x00, "switch_channel": "none"},
            "cp2": {"partno": "CAT9555", "bus": "/dev/i2c-0", "addr": 0x01, "switch_channel": "none"},
            "bit1": {"pin": 1, "chip": "cp1"},
            "bit2": {"pin": 2, "chip": "cp1"},
            "bit3": {"pin": 3, "chip": "cp1"},
            "bit17": {"pin": 1, "chip": "cp2"}
        },
        "dmm":{
            "cp3": {"partno": "CAT9555", "bus": "/dev/i2c-0", "addr": 0x02, "switch_channel": "none"},
            "bit33": {"pin": 1, "chip": "cp3"},
            "bit34": {"pin": 2, "chip": "cp3"},
            "bit35": {"pin": 3, "chip": "cp3"}
        }
    }
    '''
    _extendio = OrderedDict()
    
    ''' 
    the example of _busswitch profile
    key: the busswitch chip id or channel id
    {
            "tca9548-0": {"partno": "tca9548a", "addr": "0x70", "bus": "/dev/i2c-0", "switch_channel": "none"},
            "back-light": {"chip": "tca9548-0", "channel": 2}
    }
    '''    
    _busswitch = OrderedDict()

    ''' 
    the example of _eeprom
    key: the eeprom id
    value: the eeprom profile
    {
        "dmm": {"partno": "AT24C08ZI", "bus": "/dev/AXI4_I2C_1", "addr": 0x50, "switch_channel": "dmm_eeprom"},
        "datalogger": {"partno": "AT24C08ZI", "bus": "/dev/i2c-1", "addr": 0x50, "switch_channel": "none"}
    }
    '''
    _eeprom = OrderedDict()
    
    '''
    the example of _chips which including the base board chip but doesn't include the eeprom
    {
        "TCA9548_1":{"partno": "TCA9548", "addr": 0x71, "bus": "/dev/AXI4_EEPROM_IIC", "switch_channel": "none"},
        "psu_DAC_1":{"partno": "AD5667","addr": 0x00, "bus": "/dev/AXI4_INSTRUMENT_IIC_1", "switch_channel": "none", "vref": "2500mv"},
        "cp1":{"partno": "CAT9555","addr": 0x00, "bus": "/dev/i2c-0", "switch_channel": "none"}
    }
    '''
    _chips = OrderedDict()

    '''
    the example of _boards
    {
        "datalogger":{},
        "dmm":{}
    }
    '''
    _boards = OrderedDict()
    
    '''
    the example of _buses
    {
        'ps_i2c_0': {'path': '/dev/i2c-0', 'rate': '100000', 'type': 'i2c'},
        'UUT_UART': {'ipcore': 'Axi4Uart', 'path': '/dev/AXI4_UUT_UART', 'baudrate': '115200', 'type': 'uart'},
        'ELOAD_IIC' :{'ipcore': 'Axi4I2c', 'path': '/dev/AXI4_ELOAD_IIC', 'rate': '400000', 'type': 'i2c'}
    }
    '''
    _buses = OrderedDict()

    '''
    the example of _initconfig
    {
        "extendio":{
            "base_board_id":{
                "cp1":{"dir":[0x1f,0x0],"value":[0x0,0x0]},
                "cp2":{"dir":[0x0,0x0],"value":[0x0,0x0]}
            },
            "dmm":{
                "cp3":{"dir":[0x0,0x0],"value":[0x0,0x0]}
            }
        },
        "uart":{
            "uart_1":{"baudrate":"115200","databits":"8","stopbits":1,"parity":"none"},
            "axi4_uart_2":{"baudrate":"115200","databits":"8","stopbits":1,"parity":"none","timestamp":"none"}
        },
        "netconfig":{}
    }
    '''
    _initconfig = OrderedDict()

    '''
    the example of _ioes which including the digital io
    {
        "digital_io":[]
    }
    '''
    _ioes = OrderedDict()
    
    @classmethod
    def set_base_board_name(cls, name):
        """ set the base board name
            Args:
                name(str)   : the base board name
        """
        cls._base_board_name=name

    @classmethod
    def get_base_board_name(cls):
        """ get the base board name

            Returns:
                on success,the string of base board name will be return
                on error,will be return None
        """
        return cls._base_board_name

    @classmethod
    def get_extendio(cls):
        '''get all the extendio profile

            Returns:
                a dict of all extendio profile
        '''
        return cls._extendio
   
    @classmethod 
    def get_extendio_by_name(cls, board_name=None):
        '''get the board extendio by board id
            Args:
                board_name(str)   : the board id,default is the base board

            Returns:
                a dict of the board extendio profile
                if board_name is None,return the base board extendio profile
        '''
        if board_name == None:
            return cls._extendio[cls._base_board_name]
        else:
            return cls._extendio[board_name]

    @classmethod
    def get_extendio_chip_name(cls, bitnum, board_name=None):
        '''get the extendio chip id by bitnum id
            Args:
                bitnum(str): bitnum id
                board_name(str): the board id ,default is the base board

                Returns:
                    a string of the extendio chip id
        '''
        if board_name == None:
            return cls._extendio[cls._base_board_name][bitnum]['chip']
        else:
            return cls._extendio[board_name][bitnum]['chip']
    
    @classmethod
    def get_busswitch(cls):
        '''get all the busswitch profile

            Returns:
                a dict of all busswitch profile
        '''
        return cls._busswitch
    
    @classmethod
    def get_busswitch_by_name(cls, name):
        ''' get the busswitch by chip id or channel id
            Args:
                name(str): the chip id or channel id
            Returns:
                if name is the chip id,return the busswitch chip profile
                if name is the channel id, return the channel profile
        '''
        return cls._busswitch[name]
    
    @classmethod
    def get_eeprom(cls):
        '''get the all eeprom profile

            Returns:
                a dict of all eeprom profile
        '''
        return cls._eeprom
    
    @classmethod
    def get_eeprom_by_name(cls, name):
        '''get the eeprom profile by eeprom chip id
            Args:
                name(str): the eeprom chip id
            Returns:
                a dict of the eeprom chip profile
        '''
        return cls._eeprom[name]
    
    @classmethod
    def get_boards(cls):
        '''get all the boards profile

            Returns:
                a dict of all boards profile
        '''
        return cls._boards
    
    @classmethod
    def get_board_by_name(cls, name):
        '''get the board profile by board id
            Args:
                name(str): the board id
            Returns:
                a dict of the board profile
        '''
        return cls._boards[name]
    
    @classmethod
    def get_buses(cls):
        '''get all the buses profile

            Returns:
                a dict of all buses profile
        '''
        return cls._buses
    
    @classmethod
    def get_bus_by_name(cls, name):
        '''get the bus profile by bus id
            Args:
                name(str): the bus id
            Returns:
                the dict of the bus profile
        '''
        return cls._buses[name]
    
    @classmethod
    def get_bus_path(cls, name):
        '''get the bus device path by the bus id
            Args:
                name(str): the bus id
            Returns:
                a string of the bus device path
        '''
        return cls._buses[name]['path']

    @classmethod
    def get_bus_by_path(cls, path):
        '''get the bus profile by bus path
            Args:
                name(str): the bus id
            Returns:
                the dict of the bus profile
        '''
        if hasattr(cls,"__path_buses") is False:
            cls.__path_buses=OrderedDict()
            for name,bus in cls._buses.iteritems():
                cls.__path_buses[bus['path']]=bus
        return cls.__path_buses[path]

    @classmethod
    def get_chips(cls):
        '''get all the base board chips profile

            Returns:
                a dict of all the base board chips profile
        '''
        return cls._chips
    
    @classmethod
    def get_chip_by_name(cls, name):
        '''get the base board chip profile by chip id
            Args:
                name(str): the chip id
            Returns:
                a dict of the base board chip profile
        '''
        return cls._chips[name]
    
    @classmethod
    def get_initconfig(cls):
        '''get the initconfig profile

            Returns:
                a dict of the initconfig
        '''
        return cls._initconfig
    
    @classmethod
    def get_ioes(cls):
        '''get all the ioes profile

            Returns:
                a dict of all ioes profile
        '''
        return cls._ioes

EEDispatcher.register_method(Profile.get_extendio)
EEDispatcher.register_method(Profile.get_extendio_by_name)
EEDispatcher.register_method(Profile.get_extendio_chip_name)
EEDispatcher.register_method(Profile.get_busswitch)
EEDispatcher.register_method(Profile.get_busswitch_by_name)
EEDispatcher.register_method(Profile.get_eeprom)
EEDispatcher.register_method(Profile.get_eeprom_by_name)
EEDispatcher.register_method(Profile.get_boards)
EEDispatcher.register_method(Profile.get_board_by_name)
EEDispatcher.register_method(Profile.get_buses)
EEDispatcher.register_method(Profile.get_bus_by_name)
EEDispatcher.register_method(Profile.get_bus_path)
EEDispatcher.register_method(Profile.get_chips)
EEDispatcher.register_method(Profile.get_chip_by_name)
EEDispatcher.register_method(Profile.get_initconfig)
EEDispatcher.register_method(Profile.get_ioes)
EEDispatcher.register_method(Profile.get_base_board_name)
