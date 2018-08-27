__author__ = 'yongjiu'

from ee.profile.profile import  Profile
from ee.eedispatcher import EEDispatcher
from ee.common import logger
from ee.module.singleton_factory import SpiMasterFactory

SpiFactory = SpiMasterFactory


def spi_read(bus_name, read_length, cs_extend):
    logger.warning("spi read -->bus_name:%s, read_length:%s, cs_extend:%s "%(bus_name,read_length,cs_extend))
    """ read data in spi bus
        Args:
            bus_name: str type, spi bus id.
            read_length: int type.
            cs_extend: switch channel, default is 0
            
        Returns:
            success : return data of list type.
            if read fail, return False.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiFactory.create_object(SpiFactory, profile["path"])
        return bus.read(read_length, cs_extend)
    except Exception as e:
        logger.error("execute module spi_read False:" + repr(e))
        return False

def spi_write(bus_name, write_datas, cs_extend):
    logger.warning("spi write -->bus_name:%s, write_datas:%s, cs_extend:%s "%(bus_name,write_datas,cs_extend))
    """ write data in spi bus
        Args:
            bus_name: str type, spi bus id.
            write_datas: list type.
            cs_extend: switch channel, default is 0
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiFactory.create_object(SpiFactory, profile["path"])
        return bus.write(write_datas, cs_extend)
    except Exception as e:
        logger.error("execute module spi_write False:" + repr(e))
        return False

def spi_write_and_read(bus_name, write_datas, cs_extend):
    logger.warning("spi write and read -->bus_name:%s, write_datas:%s, cs_extend:%s "%(bus_name,write_datas,cs_extend))
    """ write data and read data at time in spi bus
        Args:
            bus_name: str type, spi bus id.
            write_datas: list type.
            cs_extend: switch channel, default is 0
            
        Returns:
            success : return data of list type.
            if read fail, return False.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiFactory.create_object(SpiFactory, profile["path"])
        return bus.write_and_read(write_datas, cs_extend)
    except Exception as e:
        logger.error("execute module spi_write_and_read False:" + repr(e))
        return False

def spi_write_to_read(bus_name, write_datas ,read_length, cs_extend):
    logger.warning("spi write to read -->bus_name:%s, write_datas:%s, read_length:%s, cs_extend:%s "%(bus_name,write_datas,read_length,cs_extend))
    """ write data to read data  in spi bus
        Args:
            bus_name: str type, spi bus id.
            write_datas: list type.
            read_length: int type
            cs_extend: switch channel, default is 0
            
        Returns:
            success : return data of list type.
            if read fail, return False.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiFactory.create_object(SpiFactory, profile["path"])
        return bus.write_to_read(write_datas, read_length, cs_extend)
    except Exception as e:
        logger.error("execute module spi_write_to_read False:" + repr(e))
        return False

def spi_config(bus_name, clk_frequency ,clk_type, wait_time_us=1,spi_clk_polarity='high'):
    logger.warning("spi config -->bus_name:%s, clk_frequency:%s, clk_type:%s, wait_time_us:%s "%(bus_name,clk_frequency,clk_type,wait_time_us))
    """ Set spi bus parameter
            
            Args:
                spi_clk_frequency(int): spi bus clock frequency, unit is Hz
                spi_clk_type(str): 'pos' --sclk posedge send data, sclk negedge receive data
                                   'neg' --sclk negedge send data, sclk posedge receive data
                wait_time_us(float):    the wait time for new spi access
                spi_clk_polarity(str): 'high' --when CS is high, the SCLK is high
                                       'low' --when CS is high, the SCLK is low
            Returns:
                None
        """ 
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiFactory.create_object(SpiFactory, profile["path"])
        return bus.config(clk_frequency, clk_type, wait_time_us,spi_clk_polarity)
    except Exception as e:
        logger.error("execute module spi_config False:" + repr(e))
        return False

def spi_disable(bus_name):
    logger.warning("spi disable -->bus name:%s "%(bus_name))
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiFactory.create_object(SpiFactory, profile["path"])
        return bus.disable()
    except Exception as e:
        logger.error("execute module spi_disable False:" + repr(e))
        return False

def spi_enable(bus_name):
    logger.warning("spi enable -->bus name:%s "%(bus_name))
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiFactory.create_object(SpiFactory, profile["path"])
        return bus.enable()
    except Exception as e:
        logger.error("execute module spi_enable False:" + repr(e))
        return False

EEDispatcher.register_method(spi_read)
EEDispatcher.register_method(spi_write)
EEDispatcher.register_method(spi_write_and_read)
EEDispatcher.register_method(spi_write_to_read)
EEDispatcher.register_method(spi_config)
EEDispatcher.register_method(spi_disable)
EEDispatcher.register_method(spi_enable)