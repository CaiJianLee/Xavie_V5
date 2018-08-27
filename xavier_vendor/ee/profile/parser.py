import json
import copy
from collections import OrderedDict

import ee.common.utility as utility
from ee.common import logger
from profile import Profile
from ee.profile.xobj import XObject

#decode unicode to utf-8
def _convert(input_value):
    if isinstance(input_value, dict):
        return {_convert(key): _convert(value) for key, value in input_value.iteritems()}
    elif isinstance(input_value, list):
        return [_convert(element) for element in input_value]
    elif isinstance(input_value, unicode):
        return input_value.encode('utf-8')
    else:
        return input_value

def _addr2hex(addr):
    if isinstance(addr, dict):
        for key, value in addr.iteritems():
            if key is 'addr':
                addr[key] = hex(addr[key])
            _addr2hex(value)

def _str_dict(input_dict):
    new_dict = copy.deepcopy(input_dict)
    _addr2hex(new_dict)
    return str(new_dict)

class ProfileParser(object):
    def __init__(self):
        self._base_board_name = None

    def read_profile(self,hardware_function_profile):
        logger.boot("start parser, profile path:%s"%(hardware_function_profile))
        try:
            profile = utility.load_json_file(hardware_function_profile,object_hook=_convert)
        except Exception as e:
            logger.boot("error: read json profile fail:%s"%(repr(e)))
            return None

        self._base_board_name = profile['base_board']['id']
        Profile.set_base_board_name(self._base_board_name)

        for bus in profile['buses']:
            bus_name = bus['id']
            try:
                self._parse_buses(bus)
            except Exception as e:
                logger.boot('error: parse the %s bus fail: %s'%(bus_name, repr(e)))
            else:
                logger.boot('parse the %s bus:%s'%(bus_name, _str_dict(Profile.get_bus_by_name(bus_name))))

        if 'netconfig' in profile.keys():
            initconfig=Profile.get_initconfig()
            initconfig['netconfig']=profile['netconfig']

        if 'digital_io' in profile.keys():
            for io in profile['digital_io']:
                io_id = io['id']
                try:
                    self._parse_digital_io(io)
                except Exception as e:
                    logger.boot("error: parse the %s digital io fail:%s"%(io_id, repr(e)))
                else:
                    logger.boot("parse the %s digital io:%s"%(io_id,Profile.get_ioes()[io_id]))

        if "chips" in profile:
            for chip in profile['chips']:
                chipname = chip['id']
                try:
                    self._parse_chips(chip)
                except Exception as e:
                    logger.boot('error: parser the  %s chip fail: %s'%(chipname, repr(e)))
                else:
                    try:
                        str_chip_profile = _str_dict(Profile.get_chip_by_name(chipname))
                    except KeyError:
                        str_chip_profile = _str_dict(Profile.get_eeprom_by_name(chipname))
                    logger.boot('parser the %s chip:%s'%(chipname, str_chip_profile))

        if "boards" in profile:
            for board in profile['boards']:
                board_name = board['id']
                if 'eeprom' in board.keys():
                    eeproms = board['eeprom']
                    if isinstance(eeproms,dict):
                        eeproms = [eeproms]

                    if isinstance(eeproms,list) is False:
                        logger.boot("error: can not parse the board eeprom,invalid format")
                    else:
                        for eeprom in eeproms:
                            try:
                                eeprom_id = eeprom["id"]
                                self._parse_eeprom(board_name, eeprom)
                            except Exception as e:
                                logger.boot('error: parser the %s board eeprom fail: %s'%(board_name,repr(e)))
                            else:
                                logger.boot('parser the %s board eeprom:%s'%(board_name, _str_dict(Profile.get_eeprom_by_name(eeprom_id))))

                try:
                    self._parse_boards(board)
                except Exception as e:
                    logger.boot('error: parse the %s board fail: %s'%(board_name, repr(e)))
                else:
                    logger.boot('parser board success, %s:%s'%(board_name,_str_dict(Profile.get_board_by_name(board_name))))

        logger.boot('parse done')
        return True

    def _parse_buses(self, bus):
        bus_name = bus['id']
        bus_type = bus['bus']
        
        buses = Profile.get_buses()
        buses[bus_name] = dict()

        for key in bus.keys():
            if key != 'id':
                buses[bus_name][key] = bus[key]

        if 'path' in bus.keys():
            buses[bus_name]['path'] = utility.get_dev_path() + '/' + bus['path']

        if bus_type == 'uart':
            initconfig = Profile.get_initconfig()
            initconfig['uart'] = initconfig.setdefault('uart', OrderedDict())
            initconfig['uart'][bus_name] = dict(baudrate=bus['baudrate'],databits=bus['databits'],stopbits=bus['stopbits'],parity=bus['parity'])
            if 'timestamp' in bus.keys():
                initconfig['uart'][bus_name]['timestamp'] = bus['timestamp']

    def _parse_boards(self, board):
        initconfig = Profile.get_initconfig()
        initconfig['boards'] = initconfig.setdefault('boards', list())
        board_name = board['id']
        partno = board['partno']
        partno_list = partno.replace('-', '_')
        method_name = 'parse_' + partno_list.lower()
        class_name = partno.replace('-', '')
        try:
            XObject.get_classes()[class_name].parse_board_profile(board)
            initconfig['boards'].append(board_name)
        except AttributeError:
            logger.boot('warning: unable to parser the %s partno of the %s board: has no the method %s'
                        %(partno,board_name,method_name))
            raise

    def _parse_chips(self, module):
        chipname = module['id']
        partno = module['partno']
        method_name = 'parse_' + partno.lower()

        try:
            XObject.get_classes()[partno].parse_chip_profile(module, self._base_board_name)
        except AttributeError:
            logger.boot('warning: unable to parser the %s partno of the %s chip: has no the method %s'
                        %(partno,chipname,method_name))
            raise

    def _parse_eeprom(self, board_name, eeprom):
        chip_id = eeprom['id']
        eeprofile = Profile.get_eeprom()
        eeprofile[chip_id] = dict()

        for key, value in eeprom.iteritems():
            eeprofile[chip_id][key] = copy.deepcopy(value)

        eeprofile[chip_id]['bus'] = Profile.get_bus_path(eeprom['bus'])
        eeprofile[chip_id]['addr'] = int(eeprom['addr'],16)
            
    def _parse_digital_io(self,profile):
        '''
        {
            "gpio_id":{"type":"gpio","path":"AXI4_GPIO_0","ipcore":"Axi4Gpio","gpio_number":"0"},

        }
        '''
        
        ioes = Profile.get_ioes()
        digital_io_id = profile['id']
        ioes[digital_io_id] = dict()
        ioes[digital_io_id] = copy.deepcopy(profile)

        ioes[digital_io_id].pop("id")

        if 'type' in profile.keys() and profile['type'] == 'gpio':
            initconfig = Profile.get_initconfig()
            initconfig['gpio'] = initconfig.setdefault('gpio', dict())
            gpio_number = int(profile['gpio_number'])
            dir_value = {'input': 1,'output': 0}
            dire = (gpio_number,dir_value[ioes[digital_io_id].pop("dir")])
            initconfig['gpio'][digital_io_id]=dict(dir=dire)
            if 'default' in profile.keys():
                value = (gpio_number,int(ioes[digital_io_id].pop("default")))
                initconfig['gpio'][digital_io_id]['value'] = value

