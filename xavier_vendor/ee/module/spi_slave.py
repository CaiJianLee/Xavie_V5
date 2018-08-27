from ee.profile.profile import  Profile
from ee.eedispatcher import EEDispatcher
from ee.common import logger
from ee.module.singleton_factory import SpiSlaveFactory


def spi_slave_read(bus_name, address, read_length):
    logger.debug("spi slave read -->bus name:%s, address:%s, read_length:%s "%(bus_name,address,read_length))
    """ read data in spi bus
        Args:
            bus_name: str type, spi bus id.
            address: int type
            read_length: int type.
            
        Returns:
            success : return data of list type.
            if read fail, return False.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiSlaveFactory.create_object(SpiSlaveFactory, profile["path"])
        return bus.register_read(address, read_length)
    except Exception as e:
        logger.error("execute module spi_slave_read False:" + repr(e))
        return False

def spi_slave_write(bus_name, address, write_data):
    logger.debug("spi slave write -->bus name:%s, address:%s, write_data:%s "%(bus_name,address,write_data))
    """ write data in spi bus
        Args:
            bus_name: str type, spi bus id.
            address: int type
            write_datas: list type.
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiSlaveFactory.create_object(SpiSlaveFactory, profile["path"])
        return bus.register_write(address, write_data)
    except Exception as e:
        logger.error("execute module spi_slave_write False:" + repr(e))
        return False

def spi_slave_config(bus_name, spi_clk_cpha_cpol = 'Mode_0',spi_byte_cfg = '1'):
    logger.debug("spi slave config -->bus name:%s, spi_clk_cpha_cpol:%s, spi_byte_cfg:%s "%(bus_name,spi_clk_cpha_cpol,spi_byte_cfg))
    """ Set spi bus parameter
            
            Args:
                spi_byte_cfg(str): '1'    --spi slave receive data or send data is 1byte
                                   '2'    --spi slave receive data or send data is 2byte
                                   '3'    --spi slave receive data or send data is 3byte
                                   '4'    --spi slave receive data or send data is 4byte
                
                spi_clk_cpha_cpol(str): 'Mode_0' --CPHA=0, CPOL=0,  when CS is high, the SCLK is low,  first edge sample
                                        'Mode_1' --CPHA=0, CPOL=1,  when CS is high, the SCLK is high, first edge sample
                                        'Mode_2' --CPHA=1, CPOL=0,  when CS is high, the SCLK is low,  second edge sample
                                        'Mode_3' --CPHA=1, CPOL=1,  when CS is high, the SCLK is high, second edge sample
            Returns:
                None
        """ 
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiSlaveFactory.create_object(SpiSlaveFactory, profile["path"])
        return bus.config(spi_clk_cpha_cpol, spi_byte_cfg)
    except Exception as e:
        logger.error("execute module spi_slave_config False:" + repr(e))
        return False

def spi_slave_disable(bus_name):
    logger.debug("spi slave disable -->bus name:%s "%(bus_name))
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiSlaveFactory.create_object(SpiSlaveFactory, profile["path"])
        return bus.disable()
    except Exception as e:
        logger.error("execute module spi_slave_disable False:" + repr(e))
        return False

def spi_slave_enable(bus_name):
    logger.debug("spi slave enable -->bus name:%s "%(bus_name))
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SpiSlaveFactory.create_object(SpiSlaveFactory, profile["path"])
        return bus.enable()
    except Exception as e:
        logger.error("execute module spi_slave_enable False:" + repr(e))
        return False

EEDispatcher.register_method(spi_slave_read)
EEDispatcher.register_method(spi_slave_write)
EEDispatcher.register_method(spi_slave_config)
EEDispatcher.register_method(spi_slave_disable)
EEDispatcher.register_method(spi_slave_enable)