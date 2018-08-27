__author__ = 'yongjiu'

from ee.profile.profile import  Profile
from ee.ipcore.axi4_sysreg import Axi4Sysreg
from ee.eedispatcher import EEDispatcher
from ee.common import logger
from ee.module.singleton_factory import HdqSlaveFactory

'''{"bus": "hdq", "id": "HDQ", "path":"AXI4_HDQ_Slave_0", "ipcore":"Axi4HdqSlave"},'''

def hdq_slave_write(bus_id, dev_addr, data):
    logger.debug("hdq slave write --> %s, %s, %s"%(bus_id, dev_addr, data))
    """ write data in hdq bus
        Args:
            bus_id: str type, hdq bus id.
            dev_addr: hex type, devixe addr.
            data: list type.
            channel: switch channel, default is None
            
        Returns:
            bool: The return value. True for success, False otherwise.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_id)
        bus = HdqSlaveFactory.create_object(HdqSlaveFactory, profile["path"])
        addr = bus.hdq_recevice_rd_addr()&0x7f
        if (addr != dev_addr):
            logger.error("recive addr error, addr:0x%02x"%addr)
            #return False
        if bus.hdq_sent_rd_data(data) is False:
            logger.error("sent data error.")
            return False
        return addr
    except Exception as e:
        logger.error("execute module hdq slave write False:" + repr(e))
        return False

def hdq_slave_read(bus_id):
    logger.debug("hdq slave read --> %s"%(bus_id))
    """ read data from hdq bus
        Args:
            bus_id: str type, hdq bus id.
            
        Returns:
            success : return tuple of (addr, data).
            if read fail, return False.
            
    """
    try:
        profile = Profile.get_bus_by_name(bus_id)
        bus = HdqSlaveFactory.create_object(HdqSlaveFactory, profile["path"])
        return (bus.hdq_receive_wr_addr(), bus.hdq_receive_wr_data())
    except Exception as e:
        logger.error("execute module hdq slave read False:" + repr(e))
        return False

EEDispatcher.register_method(hdq_slave_write)
EEDispatcher.register_method(hdq_slave_read)