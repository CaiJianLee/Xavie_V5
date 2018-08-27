__author__ = 'zhenhua'

IO_MODULE_VERSION = '1.0.0'

import re
from ee.profile.profile import Profile
import ee.overlay.extendio as Extendio

from ee.common import logger
from collections import OrderedDict
from ee.eedispatcher import EEDispatcher


def io_set(board_name, bits):
    """ Set the IO by the defined profile
        Args:
            board_name: str type ,  board name.
            bits: dict type. format: {"bitX":Y, "bitX":Y, ...} 
                        X: (1-  ) 
                        Y: 1 or 0
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
    """
    try:
        ioprofile = Profile.get_extendio_by_name(board_name)
        return Extendio.set(ioprofile, bits)
    except Exception as e:
        logger.error("execute module io io_set  error:" + repr(e))
        return False
    
def io_get(board_name, *bits):
    """ Get the IO pins state  from dev
        Args:
            board_name: str type ,  board name.
            bits: can be a multi-parameter.
                    eg: bit8, bit9,bit181 , ...
                or 
                    list type .format: ["bitX", "bitX", ...] 
                        X:(1-  )
            
        returns:
            dict type:  format:  {'bitX': Y, "bitX":Y,  ...}
                X: (1-  )
                Y: 1 or 1
            
    """
    bit_state_dict = OrderedDict()

    #logger.debug("test io")
    try:
        ioprofile = Profile.get_extendio_by_name(board_name)
        bit_state_dict = Extendio.get(ioprofile, bits)
    except Exception as e:   
        logger.error("execute module io io_get  error:" + repr(e))
        bit_state_dict["error"] = 0
        
    return bit_state_dict

    
def io_dir_set(board_name, bits):
    """ Set the IO DIR by the defined profile
        Args:
            board_name: str type ,  board name.
            bits: dict type. format: {"bitX":Y, "bitX":Y, ...} 
                        X: (1-  ) 
                        Y: 1 or 0
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
    """
    try:
        ioprofile = Profile.get_extendio_by_name(board_name)
        return Extendio.dir_set(ioprofile, bits)
    except Exception as e:
        logger.error("execute module io io_dir_set  error:" + repr(e))
        return False
        
def io_dir_get(board_name, *bits):
    """ Get the IO pins dir state  from dev
        Args:
            board_name: str type ,  board name.
            bits: can be a multi-parameter.
                    eg: bit8, bit9,bit181 , ...
                or 
                    list type .format: ["bitX", "bitX", ...] 
                        X:(1-  )
            
        returns:
            dict type:  format:  {'bitX': Y, "bitX":Y,  ...}
                X: (1-  )
                Y: 1 or 1
            
    """
    bit_state_dict = OrderedDict()

    try:
        ioprofile = Profile.get_extendio_by_name(board_name)
        bit_state_dict = Extendio.dir_get(ioprofile, bits)
    except Exception as e:   
        logger.error("execute module io io_dir_get  error:" + repr(e))
        bit_state_dict["error"] = 0
        
    return bit_state_dict


def io_chip_set(board_name, chipname, value):
    '''Set the CHIP by the defined profile
        Args:
            board_name: str type ,  board name.
           chipname: list type,  format:  ["cpX", "cpX", ...]
               X:[1-  ]  
               Which io chip  name will be set
           value:   list type, format: [[X] ,[X], ...]
                 X: list type , format: [data0,data1,...,data_n]
                        eg for X.: 
                        1.16bit:  [0xff, 0xff] 
                        2. 24bit: [0xff, 0xff, 0xff]
                eg: [[0xff,0xff],  [0x11,0x11]]
                
      Example:
            chip_set(profile , ["cp1", "cp2"], [[0xff, 0xff], [0x11, 0x11]])
            
        Returns:
            bool: The return value. True for success, False otherwise.
    '''
    if(len(chipname) != len(value)):
        logger.error("module io io_chip_set  param length error !" )
        return False
        
    try:
        ioprofile = Profile.get_extendio_by_name(board_name)
        for index in range(0, len(chipname)):
            result = Extendio.chip_set(ioprofile, chipname[index], value[index])
            if(result is False):
                logger.warning("execute module io io_chip_set False !" )
                return False
        return result
    except Exception as e:
        logger.error("execute module io io_chip_set  error:" + repr(e))
        return False
    
    
def io_chip_get(board_name, *chipname):
    """ Get the  CHIP  pins state  from dev
        Args:
            board_name: str type ,  board name.
            chipname: list type,  format:  ["cpX", "cpX", ...]
               X:[1-  ]  
               Which io chip  name state we will get .
               
        Returns:
            dict type: {"cpX": Y}, "cpX": Y, "cpX": False...}
            X:[1- ]
            Y: 16bit: [0x0000 - 0xffff]
                 24bit:[0x000000 - 0xffffff]
            
            eg: cp5 read false returns: {"cp5": False,} 
    """
    chip_state_dict = OrderedDict()
    
    ioprofile = Profile.get_extendio_by_name(board_name)
    for name in chipname:
        try:
            chip_state_dict[name] = Extendio.chip_get(ioprofile, name)
        except Exception as e:
            logger.error("execute module io io_chip_get  False:" + repr(e))
            chip_state_dict[name] = False
            
    return chip_state_dict



def io_chip_dir_set(board_name, chipname, value):
    '''Set the IO  CHIP DIR by the defined profile
        
        Args:
            board_name: str type ,  board name.
           chipname: list type,  format:  ["cpX", "cpX", ...]
               X:[1-  ]  
               Which io chip  name will be set
           value:   list type, format: [[X] ,[X], ...]
                 X: list type , format: [data0,data1,...,data_n]
                        eg for X.: 
                        1.16bit:  [0xff, 0xff] 
                        2. 24bit: [0xff, 0xff, 0xff]
                eg: [[0xff,0xff],  [0x11,0x11]]
                
      Example:
            chip_dir_set(profile , ["cp1", "cp2"], [[0xff, 0xff], [0x11, 0x11]])
            
        Returns:
            bool: The return value. True for success, False otherwise.
    '''
    if(len(chipname) != len(value)):
        logger.warning("module io io_chip_dir_set  param length error !" )
        return False
        
    try:
        ioprofile = Profile.get_extendio_by_name(board_name)
        for index in range(0, len(chipname)):
            result = Extendio.chip_dir_set(ioprofile, chipname[index], value[index])
            if(result is False):
                logger.warning("module io io_chip_dir_set  False !" )
                return False
        return result
    except Exception as e:
        logger.error("execute module io io_chip_dir_set  error:" + repr(e))
        return False


def io_chip_dir_get(board_name, *chipname):
    """ Get the  CHIP  pins dir state  from dev
        Args:
            board_name: str type ,  board name.
            chipname: list type,  format:  ["cpX", "cpX", ...]
               X:[1-  ]  
               Which io chip  name state we will get .
               
        Returns:
            dict type: {"cpX": Y}, "cpX": Y, "cpX": False...}
            X:[1- ]
            Y: 16bit: [0x0000 - 0xffff]
                 24bit:[0x000000 - 0xffffff]
            
            eg: cp5 read false returns: {"cp5": False,} 
    """
    chip_state_dict = OrderedDict()
    
    ioprofile = Profile.get_extendio_by_name(board_name)
    for name in chipname:
        try:
            chip_state_dict[name] = Extendio.chip_dir_get(ioprofile, name)
        except Exception as e:
            logger.error("execute module io io_chip_dir_get  False:" + repr(e))
            chip_state_dict[name] = False
           
    return chip_state_dict

EEDispatcher.register_method(io_set)
EEDispatcher.register_method(io_get)
EEDispatcher.register_method(io_dir_set)
EEDispatcher.register_method(io_dir_get)
EEDispatcher.register_method(io_chip_set)
EEDispatcher.register_method(io_chip_get)
EEDispatcher.register_method(io_chip_dir_set)
EEDispatcher.register_method(io_chip_dir_get)

