__author__ = 'zhenhua'

import mock
import pytest
from collections import OrderedDict 

from ee.overlay.busswitch import *
from ee.profile.profile import Profile
from ee.profile.xobj import XObject
from ee.chip.tca9548 import TCA9548
from ee.overlay.i2cbus import I2cBus
from ee.ipcore.axi4_iic import Axi4I2c

@pytest.fixture    
def use_tca9548_profile():
    profile = OrderedDict() 
    profile['tca9548-0'] = {"partno": "Cat9555", "bus": "/dev/i2c-1", "addr": 0x41, "switch_channel": "eeprom"}
    profile[ 'backlight']={"chip": "tca9548-0", "channel": 2}
    return profile

def test_get_switcher(use_tca9548_profile):
    result_switch = get_switcher(use_tca9548_profile, 'tca9548-0')
    assert result_switch == "eeprom"
        
    try:
        get_switcher(use_tca9548_profile, "backlight")
    except KeyError:
        assert True
        
    try:
        get_switcher(use_tca9548_profile, "backlight-1")
    except KeyError:
        assert True

def test_get_channel(use_tca9548_profile):
    result_switch = get_channel(use_tca9548_profile, 'backlight')
    assert result_switch == 2
        
    try:
        get_channel(use_tca9548_profile, "tca9548-0")
    except KeyError:
        assert True
        
    try:
        get_channel(use_tca9548_profile, "backlight-1")
    except KeyError:
        assert True

def test_select_busswitch():
    profile = {
                    "tca9548-0": {"partno": "tca9548a", "addr": 0x70, "bus": "/dev/i2c-0"},
                    "tca9548-2": {"partno": "tca9548a", "addr": 0x71, "bus": "/dev/i2c-1"},
                    'back-light-1':{"chip": "tca9548-0", "channel": 2},
                    'back-light-2':{"chip": "tca9548-2", "channel": 3}
    }

    with mock.patch.object(Profile, 'get_busswitch') as mock_switch_chip:
            mock_switcher = mock.Mock()
            mock_switcher.select_channel.return_value = None
            with mock.patch.object(XObject, 'get_chip_object', return_value = mock_switcher) as mock_get_class: 
                 mock_switch_chip.return_value = profile
                 
                 select_channel('back-light-1')
                 mock_switcher.select_channel.assert_called_once()
                 init_calls = [mock.call('tca9548-0')]
                 mock_get_class.assert_has_calls(init_calls)
            
                 select_channel('back-light-2')
                 assert mock_switch_chip.call_count == 2
                               
                 mock_switch_chip.reset_mock()
                 mock_switcher.reset_mock()
                 mock_switch_chip.return_value = profile
                 select_channel('back-light-2')
                 mock_switcher.select_channel.assert_called_once()


busswitch_profile = {
        "tca9548-0": {'partno':'TCA9548', 'addr': 0x71 ,'bus': "/dev/AXI4_EEPROM_IIC", 'switch_channel': 'none'},
        'tca9548-1' : {'partno':'TCA9548', 'addr': 0x72 ,'bus': "/dev/AXI4_EEPROM_IIC", 'switch_channel': 'busswitch'},
        'back-light': {'chip': 'tca9548-1', 'channel': 1},
        'busswitch': {'chip': 'tca9548-0', 'channel': 2}
}

@pytest.fixture(scope="module")
def tca9548_1():
    with mock.patch.object(Axi4I2c, '__init__', return_value=None) as mock_axi4i2c_init:
        return TCA9548(busswitch_profile['tca9548-1'])

def test_select_double_busswitch(tca9548_1):
    with mock.patch.object(Profile, 'get_busswitch') as mock_switch_chip:
        mock_switch_chip.return_value = busswitch_profile
        mock_switcher = mock.Mock()
        mock_switcher.select_channel = mock.Mock()
        with mock.patch.object(XObject, 'get_chip_object', return_value = mock_switcher) as mock_get_class: 
            select_channel('back-light')
            init_calls = [mock.call(busswitch_profile['back-light']['channel'])]
            mock_switcher.select_channel.assert_has_calls(init_calls)

            with mock.patch.object(Axi4I2c, 'write', return_value=None) as mock_axi4i2c_write:
                tca9548_1.select_channel(busswitch_profile['back-light']['channel'])
                init_calls = [mock.call(busswitch_profile['busswitch']['channel'])]
                mock_switcher.select_channel.assert_has_calls(init_calls)
                mock_axi4i2c_write.assert_called_once()



