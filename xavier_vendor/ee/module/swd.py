from ee.profile.profile import  Profile
from ee.eedispatcher import EEDispatcher
from ee.common import logger
from ee.common import utility
from ee.module.singleton_factory import SwdMasterFactory


SwdFactory = SwdMasterFactory

def swd_read(bus_id, request_data):
    logger.warning("swd read ---> %s"%list((bus_id, hex(request_data))))
    """ swd_rd_operate
        
        Args:
            request_data(byte): 8 bits
        Returns:
            False | swd_rd_data(tuple): 
                    (int read_data, char ack_data, char parity_bit)
    """ 
    try:
        profile = Profile.get_bus_by_name(bus_id)
        bus = SwdFactory.create_object(SwdFactory, profile["path"])
        frame_data = bus.swd_rd_operate(request_data)
        if frame_data is not False:
            read_data = frame_data[:4]
            ack_data = frame_data[4] & 0x07
            parity_bit = (frame_data[4] >> 7) & 0x01
            return (utility.list_convert_number(read_data), ack_data, parity_bit)
        return False
    except Exception as e:
        logger.error("execute module swd read False:" + repr(e))
        return False

def swd_write(bus_id, request_data, write_data):
    logger.warning("swd write ---> %s"%list((bus_id, request_data, hex(write_data))))
    """ swd_wr_operate
        
        Args:
            request_data(byte): 8 bits
            write_data(int): less than 32 bits
        Returns:
            False | SWD RETURN ACK DATA(byte)
    """   
    try:
        profile = Profile.get_bus_by_name(bus_id)
        bus = SwdFactory.create_object(SwdFactory, profile["path"])
        logger.warning("swd write data list---> %s"%utility.int_convert_list(write_data, 4))
        return bus.swd_wr_operate(request_data, (utility.int_convert_list(write_data, 4)))
    except Exception as e:
        logger.error("execute module swd write False:" + repr(e))
        return False

def swd_freq_set(bus_id, freq_data):
    logger.warning("swd freq set ---> %s"%list((bus_id, freq_data)))
    """ Set swd clk freq parameter
        
        Args:
            freq_data(int): swd bus clock frequency, unit is Hz
        Returns:
            None
    """ 
    try:
        profile = Profile.get_bus_by_name(bus_id)
        bus = SwdFactory.create_object(SwdFactory, profile["path"])
        return bus.swd_freq_set(freq_data)
    except Exception as e:
        logger.error("execute module swd freq set False:" + repr(e))
        return False

def swd_rst_set(bus_id,level):
    logger.warning("swd rst set ---> %s"%list((bus_id, level)))
    """ swd debug rst ctrl
        
        Args:
            level(string): 'L'--Low level,'H'--High level
        Returns:
            None
    """  
    try:
        profile = Profile.get_bus_by_name(bus_id)
        bus = SwdFactory.create_object(SwdFactory, profile["path"])
        return bus.swd_rst_pin_ctrl(level)
    except Exception as e:
        logger.error("execute module swd rst set False:" + repr(e))
        return False
    return False

def swd_timing_generate(bus_id, timing_data):
    logger.warning("swd timing generate ---> %s, len:%s"%([('0x%02x'%i) for i in timing_data], len(timing_data)))
    """ swd_switch_timing_generate
            
            Args:
                timing_data(list): timing_data, bit order: first_byte_bit0-->bit7,second_byte_bit0-->bit7,...,last_byte_bit0-->bit7
            Returns:
                False | True
    """ 
    try:
        profile = Profile.get_bus_by_name(bus_id)
        bus = SwdFactory.create_object(SwdFactory, profile["path"])
        return bus.swd_switch_timing_gen(timing_data)
    except Exception as e:
        logger.error("execute module swd rst set False:" + repr(e))
        return False
    return False

def swd_disable(bus_name):
    logger.warning("swd disable -->bus name:%s "%(bus_name))
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SwdFactory.create_object(SwdFactory, profile["path"])
        return bus.disable()
    except Exception as e:
        logger.error("execute module swd_disable False:" + repr(e))
        return False

def swd_enable(bus_name):
    logger.warning("swd enable -->bus name:%s "%(bus_name))
    try:
        profile = Profile.get_bus_by_name(bus_name)
        bus = SwdFactory.create_object(SwdFactory, profile["path"])
        return bus.enable()
    except Exception as e:
        logger.error("execute module swd_enable False:" + repr(e))
        return False

EEDispatcher.register_method(swd_write)
EEDispatcher.register_method(swd_read)
EEDispatcher.register_method(swd_freq_set)
EEDispatcher.register_method(swd_rst_set)
EEDispatcher.register_method(swd_timing_generate)
EEDispatcher.register_method(swd_disable)
EEDispatcher.register_method(swd_enable)