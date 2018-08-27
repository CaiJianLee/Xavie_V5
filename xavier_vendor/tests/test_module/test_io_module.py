
__author__ = 'zhenhua'
 
import mock
import pytest
from collections import OrderedDict 
 
import ee.overlay.extendio as Extendio
from ee.module.io import *
from ee.profile.profile import Profile
 
@pytest.fixture    
def use_cat9555_chip_profile():
    profile = OrderedDict() 
    profile ["instrument"] = {'cp1': {'partno': 'CAT9555', 'bus': '/dev/i2c-0', 'addr': 0, 'switch_channel': 'none'}, \
    'bit16': {'chip': 'cp1', 'pin': '16'},\
    'bit15': {'chip': 'cp1', 'pin': '15'},\
    'bit14': {'chip': 'cp1', 'pin': '14'},\
    'bit13': {'chip': 'cp1', 'pin': '13'},\
    'bit12': {'chip': 'cp1', 'pin': '12'},\
    'bit11': {'chip': 'cp1', 'pin': '11'},\
    'bit10': {'chip': 'cp1', 'pin': '10'},\
    'bit9': {'chip': 'cp1', 'pin': '9'},\
    'bit8': {'chip': 'cp1', 'pin': '8'},\
    'bit7': {'chip': 'cp1', 'pin': '7'},\
    'bit6': {'chip': 'cp1', 'pin': '6'},\
    'bit5': {'chip': 'cp1', 'pin': '5'},\
    'bit4': {'chip': 'cp1', 'pin': '4'},\
    'bit3': {'chip': 'cp1', 'pin': '3'},\
    'bit2': {'chip': 'cp1', 'pin': '2'},\
    'bit1': {'chip': 'cp1', 'pin': '1'}}  
    return profile

def test_io_set(use_cat9555_chip_profile):
    with mock.patch.object(Profile, 'get_extendio_by_name', return_value = use_cat9555_chip_profile["instrument"]) as mock_get_extendio:
        mock_set_result = mock.Mock()
        with mock.patch.object(Extendio, 'set', return_value = mock_set_result) as mock_set:
            io_set( "instrument",  {"bit1":1})
            mock_get_extendio.assert_called_once_with("instrument")
            mock_set.assert_called_once_with(use_cat9555_chip_profile["instrument"], {"bit1":1})

            io_set( "instrument",  {"bit1":1,"bit15":0})
            mock_get_extendio.assert_called_with("instrument")
            mock_set.assert_called_with(use_cat9555_chip_profile["instrument"], {"bit1":1,"bit15":0})
             
            assert mock_get_extendio.call_count == 2         
            assert mock_set.call_count == 2   
             
    with mock.patch.object(Extendio, 'set', return_value = []) as mock_set:
        assert False == io_set( "instrument",  {"bit2":1})  

             
def test_io_dir_set(use_cat9555_chip_profile):
    with mock.patch.object(Profile, 'get_extendio_by_name', return_value = use_cat9555_chip_profile["instrument"]) as mock_get_extendio:
        mock_set_result = mock.Mock()
        with mock.patch.object(Extendio, 'dir_set', return_value = mock_set_result) as mock_dir_set:
            io_dir_set( "instrument",  {"bit1":1})
            mock_get_extendio.assert_called_once_with("instrument")
            mock_dir_set.assert_called_once_with(use_cat9555_chip_profile["instrument"], {"bit1":1})

            io_dir_set( "instrument",  {"bit1":1,"bit15":0})
            mock_get_extendio.assert_called_with("instrument")
            mock_dir_set.assert_called_with(use_cat9555_chip_profile["instrument"], {"bit1":1,"bit15":0})
             
            assert mock_get_extendio.call_count == 2         
            assert mock_dir_set.call_count == 2   
             
    with mock.patch.object(Extendio, 'dir_set', return_value = []) as mock_dir_set:
        assert False == io_dir_set( "instrument",  {"bit2":1}) 

def test_io_get(use_cat9555_chip_profile):
    expect_result_value = {
                           "data-1":{"bit1":1},
                           "data-2":{"bit2":1,"bit15":0}
        }
    with mock.patch.object(Profile, 'get_extendio_by_name', return_value = use_cat9555_chip_profile["instrument"]) as mock_get_extendio:
        with mock.patch.object(Extendio, 'get') as mock_get:
            mock_get.return_value={"bit1":1}
            result = io_get( "instrument", *["bit1"])
            mock_get_extendio.assert_called_once_with("instrument")
            mock_get.assert_called_once_with(use_cat9555_chip_profile["instrument"], ("bit1",))
            assert result == expect_result_value["data-1"]

            mock_get.return_value={"bit2":1,"bit15":0}
            result = io_get( "instrument", *["bit2","bit15"])
            mock_get_extendio.assert_called_with("instrument")
            mock_get.assert_called_with(use_cat9555_chip_profile["instrument"], ("bit2","bit15",))
            assert result == expect_result_value["data-2"]

            assert mock_get_extendio.call_count == 2         
            assert mock_get.call_count == 2   
    with mock.patch.object(Extendio, 'get') as mock_get:
        assert {"error":0} == io_get( "instrument",  *["bit2"]) 

def test_io_dir_get(use_cat9555_chip_profile):
    expect_result_value = {
                           "data-1":{"bit1":1},
                           "data-2":{"bit2":1,"bit15":0}
        }
    with mock.patch.object(Profile, 'get_extendio_by_name', return_value = use_cat9555_chip_profile["instrument"]) as mock_get_extendio:
        with mock.patch.object(Extendio, 'dir_get') as mock_dir_get:
            mock_dir_get.return_value={"bit1":1}
            result = io_dir_get( "instrument", *["bit1"])
            mock_get_extendio.assert_called_once_with("instrument")
            mock_dir_get.assert_called_once_with(use_cat9555_chip_profile["instrument"], ("bit1",))
            assert result == expect_result_value["data-1"]

            mock_dir_get.return_value={"bit2":1,"bit15":0}
            result = io_dir_get( "instrument", *["bit2","bit15"])
            mock_get_extendio.assert_called_with("instrument")
            mock_dir_get.assert_called_with(use_cat9555_chip_profile["instrument"], ("bit2","bit15",))
            assert result == expect_result_value["data-2"]

            assert mock_get_extendio.call_count == 2         
            assert mock_dir_get.call_count == 2   
    with mock.patch.object(Extendio, 'dir_get') as mock_get:
        assert {"error":0} == io_dir_get( "instrument",  *["bit2"]) 


def test_io_chip_get(use_cat9555_chip_profile):
    expect_result_value = {
                           "data-1":{"cp1":0xffff},
                           "data-2":OrderedDict({"cp1":False,"cp2":False})
        }
    with mock.patch.object(Profile, 'get_extendio_by_name', return_value = use_cat9555_chip_profile["instrument"]) as mock_get_extendio:
        with mock.patch.object(Extendio, 'chip_get') as mock_chip_get:
            mock_chip_get.return_value = {"bit1":1,"bit2":1,"bit3":1,"bit4":1,"bit5":1,\
                                                                    "bit6":1,"bit7":1,"bit8":1,"bit9":1,"bit10":1,\
                                                                    "bit11":1,"bit12":1,"bit13":1,"bit14":1,"bit15":1,"bit16":1}
            result = io_chip_get( "instrument", *["cp1"])
            mock_get_extendio.assert_called_once_with("instrument")
            mock_chip_get.assert_called_once_with(use_cat9555_chip_profile["instrument"], "cp1")
            assert result == expect_result_value["data-1"]

            mock_chip_get.reset_mock()
            mock_chip_get.return_value = []
            result = io_chip_get( "instrument", *["cp1","cp2"])
            mock_get_extendio.assert_called_with("instrument")
            mock_chip_get.assert_any_call(use_cat9555_chip_profile["instrument"], "cp1")
            mock_chip_get.assert_any_call(use_cat9555_chip_profile["instrument"], "cp2")
            assert result == expect_result_value["data-2"]
            assert mock_chip_get.call_count == 2


def test_io_chip_dir_get(use_cat9555_chip_profile):
    expect_result_value = {
                           "data-1":{"cp1":0xffff},
                           "data-2":OrderedDict({"cp1":False,"cp2":False})
        }
    with mock.patch.object(Profile, 'get_extendio_by_name', return_value = use_cat9555_chip_profile["instrument"]) as mock_get_extendio:
        with mock.patch.object(Extendio, 'chip_dir_get') as mock_chip_dir_get:
            mock_chip_dir_get.return_value = {"bit1":1,"bit2":1,"bit3":1,"bit4":1,"bit5":1,\
                                                                    "bit6":1,"bit7":1,"bit8":1,"bit9":1,"bit10":1,\
                                                                    "bit11":1,"bit12":1,"bit13":1,"bit14":1,"bit15":1,"bit16":1}
            result = io_chip_dir_get( "instrument", *["cp1"])
            mock_get_extendio.assert_called_once_with("instrument")
            mock_chip_dir_get.assert_called_once_with(use_cat9555_chip_profile["instrument"], "cp1")
            assert result == expect_result_value["data-1"]

            mock_chip_dir_get.reset_mock()
            mock_chip_dir_get.return_value = []
            result = io_chip_dir_get( "instrument", *["cp1","cp2"])
            mock_get_extendio.assert_called_with("instrument")
            mock_chip_dir_get.assert_any_call(use_cat9555_chip_profile["instrument"], "cp1")
            mock_chip_dir_get.assert_any_call(use_cat9555_chip_profile["instrument"], "cp2")
            assert result == expect_result_value["data-2"]
            assert mock_chip_dir_get.call_count == 2

def test_io_chip_set(use_cat9555_chip_profile):
    with mock.patch.object(Profile, 'get_extendio_by_name', return_value = use_cat9555_chip_profile["instrument"]) as mock_get_extendio:
        with mock.patch.object(Extendio, 'chip_set') as mock_chip_set:
            mock_chip_set.return_value = True
            assert True == io_chip_set("instrument", ["cp1",], ([255,255],))
            mock_get_extendio.assert_called_once_with("instrument")
            mock_chip_set.assert_called_once_with(use_cat9555_chip_profile["instrument"], "cp1",[255,255])

            mock_chip_set.return_value = False
            assert False == io_chip_set("instrument", ["cp2",], ([255,255],))
            mock_get_extendio.assert_any_call("instrument")
            mock_chip_set.assert_any_call(use_cat9555_chip_profile["instrument"], "cp2",[255,255])

            assert False == io_chip_set("instrument", ["cp1","cp2"], ([255,255],))

    with mock.patch.object(Extendio, 'chip_set') as mock_chip_set:
        assert False == io_chip_set("instrument", ["cp1",], ([255,255],))  


def test_io_chip_dir_set(use_cat9555_chip_profile):
    with mock.patch.object(Profile, 'get_extendio_by_name', return_value = use_cat9555_chip_profile["instrument"]) as mock_get_extendio:
        with mock.patch.object(Extendio, 'chip_dir_set') as mock_chip_dir_set:
            mock_chip_dir_set.return_value = True
            assert True == io_chip_dir_set("instrument", ["cp1",], ([255,255],))
            mock_get_extendio.assert_called_once_with("instrument")
            mock_chip_dir_set.assert_called_once_with(use_cat9555_chip_profile["instrument"], "cp1",[255,255])

            mock_chip_dir_set.return_value = False
            assert False == io_chip_dir_set("instrument", ["cp2",], ([255,255],))
            mock_get_extendio.assert_any_call("instrument")
            mock_chip_dir_set.assert_any_call(use_cat9555_chip_profile["instrument"], "cp2",[255,255])

            assert False == io_chip_dir_set("instrument", ["cp1","cp2"], ([255,255],))

    with mock.patch.object(Extendio, 'chip_set') as mock_chip_dir_set:
        assert False == io_chip_dir_set("instrument", ["cp1",], ([255,255],))  