__author__="Haite"

from ee.profile.profile import Profile
from ee.profile.xobj import XObject
from ee.common import logger
from ee.eedispatcher import EEDispatcher

'''
 "DMM": {
    "partno": "Dmm-001-001",
    "adc": {"partno": "AD7175", "path": "/dev/AXI4_DMM_AD7175"},
    "io": {
        "BIT1": "bit81",
        "BIT2": "bit82",
        "BIT3": "bit83",
        "profile":{
            "io-1": {"partno": "CAT9555", "bus": "/dev/i2c-0", "addr": 0x40},
            "bit81": {"pin": 1, "chip": "io-1"},
            "bit82": {"pin": 2, "chip": "io-1"},
            "bit83": {"pin": 3, "chip": "io-1"}
        }
    },
    "eeprom": {"partno": "CAT24C08", "bus": "EEPROM_IIC", "switch_channel": "DMM_1","addr": "0x51"}
}
'''
def voltage_measure(name, measure_path=None):
    '''Get voltage measure channel result
    Args:
        name:the dmm board's name
        measure_path: default is None
    Returns:
        if success:
            result:(value,unit)
                value: voltage measure value
                unit: ('uV','mV','V')
        if fail:
            return False
    '''
    try:
        dmm = XObject.get_board_object(name)
        return dmm.voltage_measure()
    except Exception as e:
        logger.error("the %s board voltage_measure() execute error: %s" %(name, repr(e)))
        return False

def current_measure(name, measure_path=None):
    '''Get current measure channel result
    Args:
        name:the dmm board's name
        measure_path: default is None
    Returns:
        if success:
            result:(value,unit)
                value: current measure value
                unit: ('uA','mA','A')
        if fail:
            return False
    '''
    try:
        dmm = XObject.get_board_object(name)
        return dmm.current_measure()
    except Exception as e:
        logger.error("the %s board current_measure() execute error: %s" %(name, repr(e)))
        return False

def measure_path_set(name, measurepath):
    '''Set the dmm board measure range
    Args:
        name:the dmm board's name
        measurepath:{"channel":channel,"range":range}
            channel:["current","voltage"]
            range:
                channel="current": range=("100uA","2mA") 
                channel="voltage": range=("5V")
    Returns:
        bool: True | False, True for success, False for adc read failed
    '''
    try:
        dmm = XObject.get_board_object(name)
        return dmm.measure_path_set(measurepath)
    except Exception as e:
        logger.error("the %s board measure_path_set() measurepath:%s execute error: %s" %(name , str(measurepath), repr(e)))
        return False

def measure_path_get(name):
    '''Get the dmm board measure range
    Args:
        name:the dmm board's name

    Returns:
        if success:
            dict: {"channel":value,"range":value}
                channel:["current","voltage"]
                range:
                    channel="current": range=("100uA","2mA") 
                    channel="voltage": range=("5V")
        if fail:
            return False
    '''
    try:
        dmm = XObject.get_board_object(name)
        return dmm.measure_path_get()
    except Exception as e:
        logger.error("the %s board measure_path_get() execute error: %s" %(name,repr(e)))
        return False

def measure_path_record(name,measure_path):
    """select board measure channel path,Just record

        Args:
            name: the dmm board's name
            measure_path:{"channle":channel,"range":range}
                channel:["current","voltage"]
                range:
                    channel="current": range=("100uA","2mA") 
                    channel="voltage": range=("5V")

        Returns:
            bool: True | False, True for success, False for adc read failed
    """
    try:
        dmm = XObject.get_board_object(name)
        return dmm.measure_path_record(measure_path)
    except Exception as e:
        logger.error("the %s board measure_path_record() execute error: %s" %(name,repr(e)))
        return False

def calibration_work_mode_open(name):
    """ The board work in the calibration mode
        
        You need to enter the calibration mode,
        when you want to calibrate you results by other tools.
        The measure results of the return is original results,
        than you can use it to calculate the calibration parameters.

        Args:
            name: the dmm board's name
        Returns:
            bool: True | False, True for success, False for adc read failed
    """
    try:
        dmm = XObject.get_board_object(name)
        dmm.calibration_work_mode_open()
        return True
    except Exception as e:
        logger.error("the %s board calibration_work_mode_open() execute error: %s"%(name, repr(e)))
        return False

def calibration_work_mode_close(name):
    """The board work in normal mode,out of the calibration mode
        
        You need to out of the calibration mode,
        when you want to the result use the calibration parameters.
        The measure results of the return after calibration.

        Args:
            name: the dmm board's name
        Returns:
            bool: True | False, True for success, False for adc read failed
    """
    try:
        dmm = XObject.get_board_object(name)
        dmm.calibration_work_mode_close()
        return True
    except Exception as e:
        logger.error("the %s board calibration_work_mode_close() execute error: %s"%(name, repr(e)))
        return False

EEDispatcher.register_method(voltage_measure)
EEDispatcher.register_method(current_measure)
EEDispatcher.register_method(measure_path_set)
EEDispatcher.register_method(measure_path_get)
EEDispatcher.register_method(measure_path_record)
