__author__ = 'Mingcheng'
  
import mock
import pytest
from collections import OrderedDict 
  
import ee.overlay.extendio as Extendio
import ee.overlay.busswitch
from ee.chip.cat9555 import CAT9555
import ee.profile.profile as  Profile
  
@pytest.fixture    
def use_cat9555_chip_profile():
    profile = OrderedDict() 
    profile['io-1'] = {"partno": "CAT9555", "bus": "/dev/i2c-0", "addr": 0x40}
    profile['io-4'] = {"partno": "CAT9555", "bus": "/dev/i2c-1", "addr": 0x40}
    profile['io-5'] = {"partno": "CAT9555", "bus": "/dev/i2c-1", "addr": 0x41, "switch_channel": "backlight"}
    profile['io-10'] = {"partno": "CAT9555", "bus": "/dev/i2c-0", "addr": 0x40}
    
    profile['bit1'] = {"pin": 1, "chip": "io-1"}
    profile['bit2'] = {"pin": 2, "chip": "io-1"}
    profile['bit4'] = {"pin": 3, "chip": "io-2"}
    profile['bit5'] = {"pin": 1, "chip": "io-3"}
    profile['bit6'] = {"pin": 1, "chip": "io-4"}
    profile['bit7'] = {"pin": 2, "chip": "io-4"}
    profile['bit8'] = {"pin": 2, "chip": "io-5"}
    
    profile['bit11'] = {"pin": 1, "chip": "io-10"}
    profile['bit12'] = {"pin": 2, "chip": "io-10"}
    profile['bit13'] = {"pin": 3, "chip": "io-10"}
    profile['bit14'] = {"pin": 4, "chip": "io-10"}
    profile['bit15'] = {"pin": 5, "chip": "io-10"}
    profile['bit16'] = {"pin": 6, "chip": "io-10"}
    profile['bit17'] = {"pin": 7, "chip": "io-10"}
    profile['bit18'] = {"pin": 8, "chip": "io-10"}
    profile['bit19'] = {"pin": 9, "chip": "io-10"}
    profile['bit20'] = {"pin": 10, "chip": "io-10"}
    profile['bit21'] = {"pin": 11, "chip": "io-10"}
    profile['bit22'] = {"pin": 12, "chip": "io-10"}
    profile['bit23'] = {"pin": 13, "chip": "io-10"}
    profile['bit24'] = {"pin": 14, "chip": "io-10"}
    profile['bit25'] = {"pin": 15, "chip": "io-10"}
    profile['bit26'] = {"pin": 16, "chip": "io-10"}
    return profile
    
def test_extendio_set(use_cat9555_chip_profile):
    with mock.patch('ee.overlay.extendio.chip_get_from_dev') as mock_chip_get_from_dev:
        with mock.patch('ee.overlay.extendio.chip_set_to_dev') as mock_chip_set_to_dev:
            mock_chip_get_from_dev.return_value=65535
            Extendio.set(use_cat9555_chip_profile, {"bit1":0,"bit2":1})
            mock_chip_get_from_dev.assert_called_once_with("io-1")
            mock_chip_set_to_dev.assert_called_once_with("io-1", [254,255])

            mock_chip_get_from_dev.reset_mock()
            mock_chip_set_to_dev.reset_mock()
            mock_chip_get_from_dev.return_value=0
            Extendio.set(use_cat9555_chip_profile, {"bit1":0,"bit2":1})
            mock_chip_get_from_dev.assert_called_once_with("io-1")
            mock_chip_set_to_dev.assert_called_once_with("io-1", [2,0])
   
            mock_chip_get_from_dev.reset_mock()
            mock_chip_set_to_dev.reset_mock()
            Extendio.set(use_cat9555_chip_profile, {"bit1":0, "bit2":1, "bit6":1,"bit7":1})
            mock_chip_get_from_dev.assert_any_call("io-1")
            mock_chip_get_from_dev.assert_any_call("io-4")
            assert mock_chip_get_from_dev.call_count == 2
            assert mock_chip_set_to_dev.call_count == 2
                 
            try:
                Extendio.set(use_cat9555_chip_profile, {"bit8":0})
            except KeyError:
                assert True
         
            try:
                 Extendio.set(use_cat9555_chip_profile)
            except TypeError:
                assert True
     
            try:
                Extendio.set(use_cat9555_chip_profile,{"bit3":0})
            except KeyError:
                assert True
                 
            try:
                Extendio.set(use_cat9555_chip_profile, {"bit4":0})
            except KeyError:
                assert True
                     
            try:    
                Extendio.set(use_cat9555_chip_profile, {"bit5":0})
            except KeyError:
                assert True   
                    
            try:    
                Extendio.set(use_cat9555_chip_profile, {"bit9":0})
            except KeyError:
                assert True   


def test_extendio_get(use_cat9555_chip_profile):
    expect_value = {
        'bit1bit2': {'bit1': 1, 'bit2': 1},
        'bit6bit7': {'bit6': 0, 'bit7': 0},
        "bit1bit2bit6bit7":{'bit1': 1, 'bit2': 1,'bit6': 1, 'bit7': 1},
    }
  
    with mock.patch('ee.overlay.extendio.chip_get_from_dev') as mock_chip_get_from_dev:
        mock_chip_get_from_dev.return_value = 65535
        result_dict={}
        result_dict = Extendio.get(use_cat9555_chip_profile, ['bit1', 'bit2'])
        assert result_dict == expect_value['bit1bit2']
        mock_chip_get_from_dev.assert_called_once_with("io-1")


        mock_chip_get_from_dev.return_value = 0
        result_dict={}
        result_dict = Extendio.get(use_cat9555_chip_profile, ['bit6', 'bit7'])
        assert result_dict == expect_value['bit6bit7']
        mock_chip_get_from_dev.assert_any_call("io-4")
        assert mock_chip_get_from_dev.call_count == 2
                
        mock_chip_get_from_dev.reset_mock()
        mock_chip_get_from_dev.return_value = 65535
        result_dict={}
        result_dict = Extendio.get(use_cat9555_chip_profile, ['bit1', 'bit2','bit6', 'bit7'])
        assert result_dict == expect_value['bit1bit2bit6bit7']
             
        mock_chip_get_from_dev.reset_mock()
        mock_chip_get_from_dev.return_value = 0
        result_dict={}
        try:
            result_dict = Extendio.get(use_cat9555_chip_profile, ['bit8'])
        except KeyError:
            assert True
                
        try:
            Extendio.dir_get(use_cat9555_chip_profile, ['bit3'])
        except KeyError:
            assert True
            
        try:
            Extendio.dir_get(use_cat9555_chip_profile, ['bit4'])
        except KeyError:
            assert True
                
        try:    
            Extendio.dir_get(use_cat9555_chip_profile, ['bit5'])
        except KeyError:
            assert True     
                 
        try:    
            Extendio.dir_get(use_cat9555_chip_profile, ['bit9'])
        except KeyError:
            assert True  
                

def test_extendio_dir_set(use_cat9555_chip_profile):
    with mock.patch('ee.overlay.extendio.chip_dir_get_from_dev') as mock_chip_dir_get_from_dev:
        with mock.patch('ee.overlay.extendio.chip_dir_set_to_dev') as mock_chip_dir_set_to_dev:
            mock_chip_dir_get_from_dev.return_value=65535
            Extendio.dir_set(use_cat9555_chip_profile, {"bit1":0,"bit2":1})
            mock_chip_dir_get_from_dev.assert_called_once_with("io-1")
            mock_chip_dir_set_to_dev.assert_called_once_with("io-1", [254,255])

            mock_chip_dir_get_from_dev.reset_mock()
            mock_chip_dir_set_to_dev.reset_mock()
            mock_chip_dir_get_from_dev.return_value=0
            Extendio.dir_set(use_cat9555_chip_profile, {"bit1":0,"bit2":1})
            mock_chip_dir_get_from_dev.assert_called_once_with("io-1")
            mock_chip_dir_set_to_dev.assert_called_once_with("io-1", [2,0])
   
            mock_chip_dir_get_from_dev.reset_mock()
            mock_chip_dir_set_to_dev.reset_mock()
            Extendio.dir_set(use_cat9555_chip_profile, {"bit1":0, "bit2":1, "bit6":1,"bit7":1})
            mock_chip_dir_get_from_dev.assert_any_call("io-1")
            mock_chip_dir_get_from_dev.assert_any_call("io-4")
            assert mock_chip_dir_get_from_dev.call_count == 2
            assert mock_chip_dir_set_to_dev.call_count == 2
                 
            try:
                Extendio.dir_set(use_cat9555_chip_profile, {"bit8":0})
            except KeyError:
                assert True
         
            try:
                 Extendio.dir_set(use_cat9555_chip_profile)
            except TypeError:
                assert True
     
            try:
                Extendio.dir_set(use_cat9555_chip_profile,{"bit3":0})
            except KeyError:
                assert True
                 
            try:
                Extendio.dir_set(use_cat9555_chip_profile, {"bit4":0})
            except KeyError:
                assert True
                     
            try:    
                Extendio.dir_set(use_cat9555_chip_profile, {"bit5":0})
            except KeyError:
                assert True   
                    
            try:    
                Extendio.dir_set(use_cat9555_chip_profile, {"bit9":0})
            except KeyError:
                assert True   

def test_extendio_dir_get(use_cat9555_chip_profile):
    expect_value = {
        'bit1bit2': {'bit1': 1, 'bit2': 1},
        'bit6bit7': {'bit6': 0, 'bit7': 0},
        "bit1bit2bit6bit7":{'bit1': 1, 'bit2': 1,'bit6': 1, 'bit7': 1},
    }
  
    with mock.patch('ee.overlay.extendio.chip_dir_get_from_dev') as mock_chip_dir_get_from_dev:
        mock_chip_dir_get_from_dev.return_value = 65535
        result_dict={}
        result_dict = Extendio.dir_get(use_cat9555_chip_profile, ['bit1', 'bit2'])
        assert result_dict == expect_value['bit1bit2']
        mock_chip_dir_get_from_dev.assert_called_once_with("io-1")


        mock_chip_dir_get_from_dev.return_value = 0
        result_dict={}
        result_dict = Extendio.dir_get(use_cat9555_chip_profile, ['bit6', 'bit7'])
        assert result_dict == expect_value['bit6bit7']
        mock_chip_dir_get_from_dev.assert_any_call("io-4")
        assert mock_chip_dir_get_from_dev.call_count == 2
                
        mock_chip_dir_get_from_dev.reset_mock()
        mock_chip_dir_get_from_dev.return_value = 65535
        result_dict={}
        result_dict = Extendio.dir_get(use_cat9555_chip_profile, ['bit1', 'bit2','bit6', 'bit7'])
        assert result_dict == expect_value['bit1bit2bit6bit7']
             
        mock_chip_dir_get_from_dev.reset_mock()
        mock_chip_dir_get_from_dev.return_value = 0
        result_dict={}
        try:
            result_dict = Extendio.dir_get(use_cat9555_chip_profile, ['bit8'])
        except KeyError:
            assert True
                
        try:
            Extendio.dir_get(use_cat9555_chip_profile, ['bit3'])
        except KeyError:
            assert True
            
        try:
            Extendio.dir_get(use_cat9555_chip_profile, ['bit4'])
        except KeyError:
            assert True
                
        try:    
            Extendio.dir_get(use_cat9555_chip_profile, ['bit5'])
        except KeyError:
            assert True     
                 
        try:    
            Extendio.dir_get(use_cat9555_chip_profile, ['bit9'])
        except KeyError:
            assert True  

                
def test_extendio_chip_set(use_cat9555_chip_profile):
    with mock.patch('ee.overlay.extendio.chip_set_to_dev') as mock_chip_set_to_dev:
        Extendio.chip_set(use_cat9555_chip_profile, "io-1", [255,255])
        mock_chip_set_to_dev.assert_called_once_with("io-1",[255,255])

        mock_chip_set_to_dev.reset_mock()
        Extendio.chip_set(use_cat9555_chip_profile, "io-1", [0,0])
        mock_chip_set_to_dev.assert_called_once_with("io-1",[0,0])
        
        Extendio.chip_set(use_cat9555_chip_profile, "io-4", [0,0])
        mock_chip_set_to_dev.assert_any_call("io-4",[0,0])
        assert mock_chip_set_to_dev.call_count == 2
                    
        mock_chip_set_to_dev.reset_mock()
        Extendio.chip_set(use_cat9555_chip_profile, "io-4", [0,0,0])
        mock_chip_set_to_dev.assert_called_once_with("io-4",[0,0,0])
        
        try:
            Extendio.chip_set(use_cat9555_chip_profile, "io-3", [1,1])
        except KeyError:
            assert True
            
        try:
            Extendio.chip_set(use_cat9555_chip_profile, "io-5", [1,1])
        except KeyError:
            assert True
                  
        try:
            Extendio.chip_set(use_cat9555_chip_profile, "io-2", [255, 255])
        except KeyError:
            assert True
               
        try:
            Extendio.chip_set(use_cat9555_chip_profile, "io-10", [254,254])
        except KeyError:
            assert True

def test_extendio_chip_get(use_cat9555_chip_profile):
    expect_value = {
        "io-10":{'bit11': 1, 'bit12': 1,'bit13': 1, 'bit14': 1,'bit15': 1, 'bit16': 1,'bit17': 1, 'bit18': 1,'bit19': 1, 'bit20': 1,'bit21': 1, 'bit22': 1,'bit23': 1, 'bit24': 1,'bit25': 1, 'bit26': 1}
    }
    with mock.patch('ee.overlay.extendio.chip_get_from_dev') as mock_chip_get_from_dev:
        mock_chip_get_from_dev.return_value = 65535
        result_dict = {}
        result_dict = Extendio.chip_get(use_cat9555_chip_profile, "io-10")
        assert result_dict == expect_value['io-10']
        mock_chip_get_from_dev.assert_called_once_with("io-10")
             
        try:
            Extendio.chip_get(use_cat9555_chip_profile, "io-5")
        except KeyError:
            assert True
 
            try:
                Extendio.chip_get(use_cat9555_chip_profile, "io-2") 
            except KeyError:
                assert True

            try:
                Extendio.chip_get(use_cat9555_chip_profile, "io-3")
            except KeyError:
                assert True

def test_extendio_chip_dir_set(use_cat9555_chip_profile):
    with mock.patch('ee.overlay.extendio.chip_dir_set_to_dev') as mock_chip_dir_set_to_dev:
        Extendio.chip_dir_set(use_cat9555_chip_profile, "io-1", [255,255])
        mock_chip_dir_set_to_dev.assert_called_once_with("io-1",[255,255])

        mock_chip_dir_set_to_dev.reset_mock()
        Extendio.chip_dir_set(use_cat9555_chip_profile, "io-1", [0,0])
        mock_chip_dir_set_to_dev.assert_called_once_with("io-1",[0,0])
        
        Extendio.chip_dir_set(use_cat9555_chip_profile, "io-4", [0,0])
        mock_chip_dir_set_to_dev.assert_any_call("io-4",[0,0])
        assert mock_chip_dir_set_to_dev.call_count == 2
                    
        mock_chip_dir_set_to_dev.reset_mock()
        Extendio.chip_dir_set(use_cat9555_chip_profile, "io-4", [0,0,0])
        mock_chip_dir_set_to_dev.assert_called_once_with("io-4",[0,0,0])
        
        try:
            Extendio.chip_dir_set(use_cat9555_chip_profile, "io-3", [1,1])
        except KeyError:
            assert True
            
        try:
            Extendio.chip_dir_set(use_cat9555_chip_profile, "io-5", [1,1])
        except KeyError:
            assert True
                  
        try:
            Extendio.chip_dir_set(use_cat9555_chip_profile, "io-2", [255, 255])
        except KeyError:
            assert True
               
        try:
            Extendio.chip_dir_set(use_cat9555_chip_profile, "io-10", [254,254])
        except KeyError:
            assert True

def test_extendio_chip_dir_get(use_cat9555_chip_profile):
    expect_value = {
        "io-10":{'bit11': 1, 'bit12': 1,'bit13': 1, 'bit14': 1,'bit15': 1, 'bit16': 1,'bit17': 1, 'bit18': 1,'bit19': 1, 'bit20': 1,'bit21': 1, 'bit22': 1,'bit23': 1, 'bit24': 1,'bit25': 1, 'bit26': 1}
    }
    with mock.patch('ee.overlay.extendio.chip_dir_get_from_dev') as mock_chip_dir_get_from_dev:
        mock_chip_dir_get_from_dev.return_value = 65535
        result_dict = {}
        result_dict = Extendio.chip_dir_get(use_cat9555_chip_profile, "io-10")
        assert result_dict == expect_value['io-10']
        mock_chip_dir_get_from_dev.assert_called_once_with("io-10")
             
        try:
            Extendio.chip_dir_get(use_cat9555_chip_profile, "io-5")
        except KeyError:
            assert True

        try:
            Extendio.chip_dir_get(use_cat9555_chip_profile, "io-2")
        except KeyError:
            assert True

        try:
            Extendio.chip_dir_get(use_cat9555_chip_profile, "io-3")
        except KeyError:
            assert True
