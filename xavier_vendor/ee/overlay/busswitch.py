__author__='Mingcheng'

from ee.profile.profile import  Profile
from ee.profile.xobj import XObject
from ee.common import logger

def get_switcher(profile, channel_name):
    """ from profile  get switcher opject  
        
        Args:
            profile: Dictionary of the hardware profile.
            channel_name: which channel   will be select, check it in profile. for example:'back-light.
            
        Returns:
            class:  return  a switcher from  profile.
            
    """    
#     chip_name = profile[channel_name]['chip']
#     chip = profile[chip_name]
#     switcher = Profile.get_class(chip['partno'], chip['bus'], chip['addr'])
#     return switcher
    switcher = profile[channel_name]['switch_channel']
    return switcher

def get_channel(profile, channel_name):
    """ from profile  get channel  
        
        Args:
            profile: Dictionary of the hardware profile.
            channel_name: which channel   will be select, check it in profile. for example:'back-light.
            
        Returns:
            str:  return  a channel from profile.  
            
         Raises:
            KeyError: If the key is invalid.
    """    
    return profile[channel_name]['channel']

#def get_chip(profile, channel_name):
#    chip_name = profile[channel_name]['chip']
#    return profile[chip_name]

#def select_channel_by_profile(channel_name):
def select_channel(channel_name):
    """ select which channel to operate
        
        Args:
        channel_name: which channel   will be select, check it in profile. for example:'back-light
            
        Returns:
            object:  return  switch object.
                    
        Raises:
            KeyError: If the key is invalid.    
            ValueError: If the parameter is invalid
    """
    busswitch = Profile.get_busswitch()
    chipname = busswitch[channel_name]['chip']
    channel = busswitch[channel_name]['channel']
    
    switcher = XObject.get_chip_object(chipname)
    if switcher.select_channel(channel) is False:
        logger.warning("select %s channel %s fail" %(chipname, channel_name))

    return switcher
   
def select_multi_channels(*channel_names): 
    pass
    