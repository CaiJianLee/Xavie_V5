#!/usr/bin/python
#-*- coding: UTF-8 -*-
import os
import time
import zmq,sys
import traceback
from threading import Thread
sys.path.append('/opt/seeing/app/ee')
import ee.module
from ee.common import logger
from ee.common import utility
from ee.tinyrpc.transports.zmq import ZmqServerTransport
from ee.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from ee.tinyrpc.server import RPCServer
from ee.eedispatcher import EEDispatcher
from ee.profile.parser import ProfileParser
from ee.bus.gpio import  GPIO,SeGpioFaultError
from ee.common import daemon
import ee.initializer
from ee import uart_server
from ee.profile.xobj import XObject
from ee.bus.uart import UartBus
from ee.ipcore.axi4_uart import Axi4Uart
from ee.chip import *
from ee.board import *

__version__ = '1.0.0'

class EmbeddedEngine(Thread):

    def __init__(self, publisher=None, stop_on_fail=False):
        super(EmbeddedEngine, self).__init__()

        if publisher:
            self.transport = publisher
        else:
            ctx = zmq.Context()
            self.transport = ZmqServerTransport.create(ctx, 'tcp://*:22702')
        
        self.dispatcher = EEDispatcher(self.transport)
        self.dispatcher.register_public_methods()

        #give the publisher sometime
        time.sleep(1)

        self.rpc_server = RPCServer(
            self.transport,
            JSONRPCProtocol(),
            self.dispatcher,
        )

    def add_methods(self):
        self.dispatcher.register_public_methods()

    def run(self):
        logger.boot('embedded engine starting')
        while True:
            try:
                self.rpc_server.serve_forever()
            except Exception:
                logger.warning("rpc server exception: %s"%(traceback.format_exc()))

        logger.info("embedded engine stopping")

if __name__ == '__main__':
    utility.register_signal_handle()
    ee_daemon = daemon.Daemon("ee1")
    ee_daemon.start()
    logger.init("ee1.log")
    logger.setLevel('WARNING')

    '''
    解决在xobj模块中引用chip和board类导致相互引用错误
    '''
    classes = globals()
    XObject.set_classes(classes)

    jsonfile = "/opt/seeing/app/b31_bp/Hardware_Function_Profile2.json"
    parser = ProfileParser()
    try:
        parser.read_profile(jsonfile)
    except Exception:
        logger.warning("profile read: %s"%(traceback.format_exc()))
        #print 'error parser profile fail'
        os._exit(ret)

    ret = ee.initializer.init()
    if ret is False:
        logger.boot("init project fail")
        #os._exit(ret)
    ee = EmbeddedEngine()
    ee.run()

