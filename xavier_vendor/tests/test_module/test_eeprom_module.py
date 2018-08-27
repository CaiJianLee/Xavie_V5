
__author__ = 'zhenhua'
 
import mock
import pytest
from collections import OrderedDict 
 
import ee.overlay.eeprom as Eeprom
from ee.module.eeprom import *
from ee.profile.profile import Profile
 
@pytest.fixture    
def use_dmm_profile():
    profile = OrderedDict()  
    profile ["dmm-module-1"] = {"bus": "/dev/i2c-0", "addr": "0x50", "switcher": "dmm", "partno": "CAT24C08ZI"}  
#     profile ["dmm-module-2"] = {"bus": "/dev/i2c-0", "addr": "0x52", "switcher": "dmm", "partno": "CAT24C08ZI"}  
    return profile
 
def test_eeprom_write(use_dmm_profile):
    with mock.patch.object(Profile, 'get_eeprom_by_name', return_value = use_dmm_profile) as mock_get_eeprom:
        mock_switcher = mock.Mock()
        with mock.patch.object(Eeprom, 'write', return_value = mock_switcher) as mock_write:
            eeprom_write( "dmm-module-1",  "0x01", 1)
            mock_get_eeprom.assert_called_once_with("dmm-module-1")
            mock_write.assert_called_once_with(use_dmm_profile, "0x01", 1)
             
            eeprom_write( "dmm-module-1",  "0x02", 5)            
            mock_get_eeprom.assert_called_with("dmm-module-1")
            mock_write.assert_called_with(use_dmm_profile, "0x02", 5)
            assert mock_get_eeprom.call_count == 2         
            assert mock_write.call_count == 2   
             
    with mock.patch.object(Eeprom, 'write', return_value = []) as mock_write:
        assert False == eeprom_write( "dmm-module-1",  "0x02", 5)  

             
             
def test_eeprom_read(use_dmm_profile):
    expect_return_value = {
                           "data-1":[1,1],
                           "data-2":[2,2]
        }
    with mock.patch.object(Profile, 'get_eeprom_by_name') as mock_get_eeprom:
        with mock.patch.object(Eeprom, 'read') as mock_read:
            mock_get_eeprom.return_value = use_dmm_profile
             
            mock_read.return_value = [1,1]
            result = []
            result = eeprom_read("dmm-module-1",  "0x01", 2)
            assert result == expect_return_value["data-1"]
            mock_get_eeprom.assert_called_once_with("dmm-module-1")
            mock_read.assert_called_once_with(use_dmm_profile, "0x01", 2)
             
            mock_read.return_value = [2,2]
            result = []
            result = eeprom_read("dmm-module-1",  "0x02", 2)
            assert result == expect_return_value["data-2"]       
                
            mock_read.return_value = [3,2]
            result = []
            result = eeprom_read("dmm-module-1",  "0x01", 2)
            assert result != expect_return_value["data-1"]                      
            assert result != expect_return_value["data-2"]     
                            
            mock_get_eeprom.assert_called_with("dmm-module-1")
            mock_read.assert_called_with(use_dmm_profile, "0x01", 2)
            assert mock_get_eeprom.call_count == 3         
            assert mock_read.call_count == 3       
             

    with mock.patch.object(Eeprom, 'read', return_value = []) as mock_read:
        assert False == eeprom_read( "dmm-module-1",  "0x02", 5)  
