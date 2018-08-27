__author__ = 'zhenhua'

from ee.profile.profile import  Profile
from ee.overlay.i2cbus import I2cBus
from ee.eedispatcher import EEDispatcher
from ee.common import logger
from ee.module.singleton_factory import I2cMasterFactory

def i2c_write(bus_id, dev_addr, data, channel = None):
    """ write data in i2c bus
        Args:
            bus_id: str type, i2c bus id.
            dev_addr: hex type, devixe addr.
            data: list type.
            channel: switch channel, default is None
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_id)
        channel = 'none' if channel == None else channel
        #bus = I2cBus(profile["path"], channel)
        bus = I2cMasterFactory.create_object(I2cMasterFactory, profile["path"], channel)
        return bus.write(dev_addr, data)
    except Exception as e:
        logger.error("execute module i2c write False:" + repr(e))
        return False

def i2c_read(bus_id, dev_addr, length, channel = None):
    """ read data from i2c bus
        Args:
            bus_id: str type, i2c bus id.
            dev_addr: hex type, devixe addr.
            length: int type. 
            channel: switch channel, default is None
            
        Returns:
            success : return data of list type.
            if read fail, return False.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_id)
        channel = 'none' if channel == None else channel
        #bus = I2cBus(profile["path"], channel)
        bus = I2cMasterFactory.create_object(I2cMasterFactory, profile["path"], channel)
        return bus.read(dev_addr, length)
    except Exception as e:
        logger.error("execute module i2c read False:" + repr(e))
        return False

def i2c_rdwr(bus_id, dev_addr, write_data, read_length, channel = None):
    """ write_data is a data list , read_lenght ,the size of your will read
        Args:
            bus_id: str type, i2c bus id.
            dev_addr: hex type, devixe addr.
            write_data: list type.
            read_length: int type. 
            channel: switch channel, default is None

        Returns:
            success : return data of list type.
            if read fail, return False.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_id)
        channel = 'none' if channel == None else channel
        #bus = I2cBus(profile["path"], channel)
        bus = I2cMasterFactory.create_object(I2cMasterFactory, profile["path"], channel)
        return bus.rdwr(dev_addr, write_data, read_length)
    except Exception as e:
        logger.error("execute module i2c rdwr False:" + repr(e))
        return False

def i2c_config(bus_id, rate):
    logger.debug("bus:%s, rate:%s"%(bus_id, rate))
    """ 
        Args:
            bus_id: str type, i2c bus id.
            rate: int type.

        Returns:
            return None

    """
    try:
        profile = Profile.get_bus_by_name(bus_id)
        #bus = I2cBus(profile["path"])
        bus = I2cMasterFactory.create_object(I2cMasterFactory, profile["path"])
        return bus.config(rate)
    except Exception as e:
        logger.error("execute module i2c config False:" + repr(e))
        return False

def i2c_crol(bus_id, state):
    logger.debug("bus:%s, state:%s"%(bus_id, state))
    """ 
        Args:
            bus_id: str type, i2c bus id.
            state: (0,1),0:disable 1:enable.

        Returns:
            return None

    """
    try:
        profile = Profile.get_bus_by_name(bus_id)
        #bus = I2cBus(profile["path"])
        bus = I2cMasterFactory.create_object(I2cMasterFactory, profile["path"])
        if state == 0:
            logger.error("i2c_crol disable")
            return bus.disable()
        else:
            return bus.enable()
    except Exception as e:
        logger.error("execute module i2c crol False:" + repr(e))
        return False

EEDispatcher.register_method(i2c_write)
EEDispatcher.register_method(i2c_read)
EEDispatcher.register_method(i2c_rdwr)
EEDispatcher.register_method(i2c_config)
EEDispatcher.register_method(i2c_crol)
