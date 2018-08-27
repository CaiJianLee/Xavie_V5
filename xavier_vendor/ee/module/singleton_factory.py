''' create singleton-object by using these factorys '''

import os
from ee.common import logger
from ee.ipcore.axi4_spi_slave import Axi4SpiSlave
from ee.ipcore.axi4_spi import Axi4Spi
from ee.ipcore.axi4_swd_core import Axi4SwdCore
from ee.ipcore.axi4_hdq_slave import Axi4HdqSlave
from ee.overlay.i2cbus import I2cBus


def get_objectname_by_path(path):
    dirname,basename = os.path.split(path)
    return "static_object_%s"%(basename)


class SingletonFactory(object):
    object_type = 'object_class_name'

    @staticmethod
    def init_object(object_class):
        object_class.disable()
        object_class.enable()

    @staticmethod
    def create_object(self, path):
        object_name = get_objectname_by_path(path)
        if getattr(self, object_name, None) == None:
            logger.debug("create new object:%s"%(object_name))
            setattr(self, object_name, eval(self.object_type)(path))
            ''' init object'''
            self.init_object(getattr(self, object_name))
            ''' init end'''
        logger.debug("get object:%s"%(getattr(self, object_name)))
        return getattr(self, object_name)

    @staticmethod
    def delete_object(self, path):
        object_name = get_basename_by_path(path)
        if getattr(self, object_name, None) != None:
            logger.debug("delete object:%s"%(object_name))
            setattr(self, object_name, None)
            logger.debug('after delete object:%s'%(getattr(self, object_name)))
        return None


class SwdMasterFactory(SingletonFactory):
    object_type = 'Axi4SwdCore'


class SpiMasterFactory(SingletonFactory):
    object_type = 'Axi4Spi'


class SpiSlaveFactory(SingletonFactory):
    object_type = 'Axi4SpiSlave'


class HdqSlaveFactory(SingletonFactory):
    object_type = 'Axi4HdqSlave'


class I2cMasterFactory(SingletonFactory):
    object_type = 'I2cBus'

    @staticmethod
    def init_object(object_class, channel):
        object_class._channel = None if channel == 'none' else channel

    @staticmethod
    def create_object(self, path, channel = None):
        object_name = get_objectname_by_path(path)
        if getattr(self, object_name, None) == None:
            logger.debug("create new object:%s"%(object_name))
            setattr(self, object_name, eval(self.object_type)(path, channel))
        logger.debug("get object:%s"%(getattr(self, object_name)))
        ''' init '''
        self.init_object(getattr(self, object_name), channel)
        ''' init end '''
        return getattr(self, object_name)