#-*- coding: UTF-8 -*-
from collections import OrderedDict 
from ee.profile.xobj import XObject
import ee.common.utility as utility

def set(profile, bits):
    """ Set the IO by the defined profile
        Args:
            profile: Dictionary of the hardware profile
            bits: dict type. format: {"bitX":Y, "bitX":Y, ...} 
                X: (1-  ) 
                Y: 1 or 0
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
        Raises:
            KeyError: If the key is invalid.
    """
            
    return _io_set(profile, bits, chip_get_from_dev, chip_set_to_dev)
    
def get(profile, bits):
    """ Get the IO pins state  from dev
        Args:
            profile: Dictionary of the hardware profile
            bits: list type .format: ["bitX", "bitX", ...] 
                X:(1-  )
            
        returns:
            dict type:  format:  {'bitX': Y, "bitX":Y,  ...}
                X: (1-  )
                Y: 1 or 1
            
        Raises:
            KeyError: If the key is invalid.
    """
    
    return _io_get(profile, bits, chip_get_from_dev)
    
def dir_set(profile, bits):
    """ Set the IO DIR by the defined profile
        Args:
            profile: Dictionary of the hardware profile
            bits: dict type. format: {"bitX":Y, "bitX":Y, ...} 
                X: (1-  ) 
                Y: 1 or 0
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
        Raises:
            KeyError: If the key is invalid.
    """
            
    return _io_set(profile, bits, chip_dir_get_from_dev, chip_dir_set_to_dev)

def dir_get(profile, bits):
    """ Get the IO pins dir state  from dev
        Args:
            profile: Dictionary of the hardware profile
            bits: list type .format: ["bitX", "bitX", ...] 
                X:(1-  )
            
        returns:
            dict type:  format:  {'bitX': Y, "bitX":Y,  ...}
                X: (1-  )
                Y: 1 or 1
            
        Raises:
            KeyError: If the key is invalid.
    """
    
    return _io_get(profile, bits, chip_dir_get_from_dev)
        
def chip_set(profile,  chipname, value):
    '''Set the CHIP by the defined profile
        Args:
            profile: Dictionary of the hardware profile
           chipname: string type,  format:  "cpX"
               X:[1-  ]  
               Which io chip  name will be set
           value:   list type, format: [data0,data1,...,data_n]
                eg.: 
                1.16bit:  [0xff, 0xff] 
                2. 24bit: [0xff, 0xff, 0xff]
        
      Example:
            chip_set(profile , "cp1", [0xff, 0xff])
            
        Returns:
            bool: The return value. True for success, False otherwise.
        Raises:
            KeyError: If the key is invalid.   
    '''
    
    return chip_set_to_dev(chipname, value)
    

def chip_get(profile, chipname):
    """ Get the  CHIP  pins state  from dev
        Args:
            profile: Dictionary of the hardware profile
            chipname: string type,  format:  "cpX"
               X:[1-  ]  
               Which io chip  name state we will get .
               
        Returns:
            int type.
            
        Raises:
            KeyError: If the key is invalid.
    """    
    
    return _io_chip_get(profile, chipname, chip_get_from_dev)
    
def chip_dir_set(profile,  chipname, value):
    '''Set the IO  CHIP DIR by the defined profile
        
        Args:
            profile: Dictionary of the hardware profile
           chipname: string type,  format:  "cpX"
               X:[1-  ]  
               Which io chip  name will be set .
           value: list type. format: [data0,data1,...,data_n]
                eg.: 
                1.16bit:  [0xff, 0xff] 
                2. 24bit: [0xff, 0xff, 0xff]
        
      Example:
            chip_dir_set(profile , "cp1", [0xff, 0xff])
            
        Returns:
            bool: The return value. True for success, False otherwise.
        Raises:
            KeyError: If the key is invalid.   
    '''
    
    return   chip_dir_set_to_dev(chipname, value)

def chip_dir_get(profile, chipname):
    """ Get the  CHIP  pins dir state  from dev
        Args:
            profile: Dictionary of the hardware profile
            chipname: string type,  format:  "cpX"
               X:[1-  ]  
               Which io chip  name  state we will  get .
               
        Returns:
            int type.

            
        Raises:
            KeyError: If the key is invalid.
    """
    return _io_chip_get(profile, chipname, chip_dir_get_from_dev)
                    
                    
def _io_set(profile, bits, cb_get, cb_set):
    result = False
    pins = OrderedDict()
    chip_state = 0
    
    for key, value in bits.items():
        chipname = profile[key]['chip']
        if chipname not in pins.keys():
            pins[chipname] = []
        pins[chipname].append((profile[key]['pin'], value))
    
    for chipname in pins.keys():
        state = cb_get(chipname)
        if False == state:
            return False
        length = len(state)
        chip_state = utility.list_convert_number(state)
        for bit_list in pins[chipname]:
            chip_state = chip_state&(~(1<<(int(bit_list[0])-1)))|(int(bit_list[1])<<(int(bit_list[0])-1))
                
        register_status = utility.int_convert_list(chip_state, length)

        result = cb_set(chipname, register_status)
            
    return result

def _io_get(profile, bits, cb_get):
    chips = OrderedDict()
    result_dict = OrderedDict()
    chip_state = 0
    
    for key in bits:
        chipname = profile[key]['chip']
        if chipname not in chips.keys():
            chips[chipname] = []
        chips[chipname].append((key, profile[key]['pin']))
           
    for chipname in chips.keys():
    
        chip_state = cb_get(chipname)
        if False == chip_state:
            return False

        chip_state = utility.list_convert_number(chip_state)

        for bit_num in chips[chipname]:
            bit_state = (chip_state>>(int(bit_num[1])-1)) & 1
            result_dict[bit_num[0]] = bit_state
             
    return result_dict

def _io_chip_get(profile, chipname, cb_get):
    chips = OrderedDict()
    chips[chipname] = []
    bitname_list=[]
    
    for bitname in profile:
        try:
            if(profile[bitname]["chip"] == chipname):
                chips[chipname].append((bitname,profile[bitname]["pin"]))
                bitname_list.append(bitname)
        except BaseException as e:
            continue    
     
    input_output_status = cb_get(chipname)
    if False == input_output_status:
        return False
    return utility.list_convert_number(input_output_status)
     

def chip_get_from_dev(name):
    chip = XObject.get_chip_object(name)
    if chip is not None:
        return chip.read_out_in_state()
        # state = utility.list_convert_number(input_output_status)
        # return state
    else:
        return False
    
def chip_dir_get_from_dev(name):
    chip = XObject.get_chip_object(name)
    if chip is not None:
        return chip.read_dir_config()
        # state = utility.list_convert_number(input_output_status)
        # return state
    else:
        return False

def chip_set_to_dev(name,value): 
    chip = XObject.get_chip_object(name)
    if chip is not None:
        return chip.write_outport(value)
    else:
        return False

def chip_dir_set_to_dev(name, value):
    chip = XObject.get_chip_object(name)
    if chip is not None:
        return  chip.write_dir_config(value) 
    else:
        return False