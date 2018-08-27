__author__=''
from ee.profile.xobj import XObject

def write(profile, addr, data):
    """ write  a list data  by the defined profile
        
        Args:
            profile: Dictionary of the hardware profile.
            addr: which  addr will be write data in. 
            data: data type is list.
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
        Raises:
            KeyError: If the key is invalid.
    """
    eeprom = XObject.get_object(profile['partno'], profile)
    return eeprom.write(addr,data)
        
def read(profile, addr, length):
    """ read  data  by the defined profile
        
        Args:
            profile: Dictionary of the hardware profile.
            addr: which  addr will be write data in. 
            length: Want to get the length of the data.
            
        Returns:
            list: success  return datas which beed  saved in a list. False otherwise.
            
        Raises:
            KeyError: If the key is invalid.
    """
    eeprom = XObject.get_object(profile['partno'], profile)
    return eeprom.read(addr,length)
