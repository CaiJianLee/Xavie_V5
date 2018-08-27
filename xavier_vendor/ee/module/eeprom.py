from ee.profile.profile import  Profile
import ee.overlay.eeprom as Eeprom
from ee.eedispatcher import EEDispatcher
from ee.common import logger

def eeprom_write(module_name, addr, data):
    """ write  a list data  by the defined profile
        
        Args:
            module_name: the key of Dictionary which can get the hardware profile.for example: "dmm-module-1"
            addr: which  addr will be write data in. 
            data: data type is list.
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
    """
    try:
        profile = Profile.get_eeprom_by_name(module_name)
        result =  Eeprom.write(profile, addr, data)
    except Exception as e:
        logger.error("execute module  eeprom_write  False:" + repr(e))
        return False
    return result

def eeprom_read(module_name, addr, length):
    """ read   data  by  the defined profile
        
        Args:
            module_name: the key of Dictionary which can get the hardware profile.for example: "dmm-module-1"
            addr:  read data from this addr.
            length: read data length.
            
        Returns:
            list: success  return data which beed  saved in a list. False otherwise.
            
    """
    try:
        profile = Profile.get_eeprom_by_name(module_name)
        result =  Eeprom.read(profile, addr, length)
    except Exception as e:
        logger.error("execute module  eeprom_read  False:" + repr(e))
        return False
    return result

EEDispatcher.register_method(eeprom_write)
EEDispatcher.register_method(eeprom_read)
