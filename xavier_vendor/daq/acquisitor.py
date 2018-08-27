#!/usr/bin/python
import zmq
import ctypes
from threading import Thread
import ee.common.utility as utility
from ee.common import logger

libdaq = ctypes.cdll.LoadLibrary(utility.get_lib_path() + "/libsgdaq.so")

class DAQ(ctypes.Structure):
    __fields__ = [
        ("axis_dev",  ctypes.c_void_p)
    ]

class DataAcquisitor(Thread):
    def __init__(self, devpath):
        super(DataAcquisitor, self).__init__()
        self._dma_path = ctypes.c_char_p(devpath)
    
    def run(self):
        logger.init("daq.log")
        libdaq.sg_daq_create.restype = ctypes.POINTER(DAQ)
        daq = libdaq.sg_daq_create(self._dma_path, 0x7000000)
        if not daq:
            logger.boot("create daq failed")
            return None

        logger.boot("the data acquisitor is running")
        libdaq.sg_daq_run(daq) 


class DataAcquisitorEx(Thread):
    def __init__(self, devpath):
        super(DataAcquisitorEx, self).__init__()
        self._dma_path = ctypes.c_char_p(devpath)
    
    def run(self):
        logger.init("daq.log")
        libdaq.sg_daq_create.restype = ctypes.POINTER(DAQ)
        daq = libdaq.sg_daq_create(self._dma_path, 0x7000000)
        if not daq:
            logger.boot("create daq failed")
            return None

        logger.boot("the data acquisitor is running")
        libdaq.sg_daqex_run(daq) 