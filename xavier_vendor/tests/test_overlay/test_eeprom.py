__author__ = 'zhenhua'

import mock
import pytest
from collections import OrderedDict 

import ee.overlay.eeprom as Eeprom
import ee.overlay.busswitch as BusSwitch
from ee.overlay.eeprom import *
from ee.profile.xobj import XObject
     
dmm_module_profile = {
        "dmm-module": {"bus": "/dev/i2c-0", "addr": "0x50", "switch_channel": "dmm", "partno": "CAT24C08ZI"},
        "dmm-module-1": {"bus": "/dev/i2c-1", "addr": "0x51", "partno": "CAT24C08ZI-1"},
        "dmm-module-2": {"bus": "/dev/i2c-1", "addr": "0x51"}
}  

    
def test_write():
    mock_class = mock.Mock()
    with mock.patch.object(XObject, 'get_object', return_value = mock_class) as mock_get_object:
        write(dmm_module_profile["dmm-module-1"]  ,  0x01, 2)            
        init_calls = [mock.call("CAT24C08ZI-1", {'partno': 'CAT24C08ZI-1', 'bus': '/dev/i2c-1', 'addr': '0x51'})]
        mock_get_object.assert_has_calls(init_calls)            
        
        
        try:
            write(dmm_module_profile[ "dmm-module-2"], 0x02, 2 )
        except KeyError:
            assert True

        try:
            write(dmm_module_profile[ "dmm-module-5"], 0x02, 2 )
        except KeyError:
            assert True
        
            
def test_read(): 
    expect_return_value = {
                           "data-1":[1,1],
                           "data-2":[2,2]
        }

    mock_class = mock.Mock()
    mock_class.read.return_value = [1,1]
    with mock.patch.object(XObject, 'get_object', return_value = mock_class) as mock_get_object:      
  
        result = read(dmm_module_profile["dmm-module-1"] ,  0x21, 1)          
        assert result == expect_return_value["data-1"]
        init_calls = [mock.call("CAT24C08ZI-1", {'partno': 'CAT24C08ZI-1', 'bus': '/dev/i2c-1', 'addr': '0x51'})]
        mock_get_object.assert_has_calls(init_calls)     
          
        try:
            read(dmm_module_profile[ "dmm-module-2"], 0x02, 2 )
        except KeyError:
            assert True      
                   
        try:
            write(dmm_module_profile[ "dmm-module-5"], 0x02, 2 )
        except KeyError:
            assert True