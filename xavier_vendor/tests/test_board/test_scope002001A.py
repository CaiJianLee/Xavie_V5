import pytest
import mock
from ee.board.scope002.scope002001A import Scope002001A
from ee.chip.ad7177 import AD7177


_scope002_profile ={
    "partno": "Scope-002-001A", 
    "id": "datalogger",
     "daq_channel":[
            {"type": "datalogger", "ch": 0, "id": "current", "port": 7604, "chipnum": 1, "filters": ["output"]},
            {"type": "datalogger", "ch": 1, "id": "voltage", "port": 7603, "chipnum": 1, "filters": ["output"]}
        ],
    "adc": {"partno": "AD7177", "path": "AXI4_DATALOGGER_AD7177", "samplerate": "1000Hz", "vref": "2500mV", "chipnum": 1},
    "eeprom": {"partno": "CAT24C08", "bus": "EEPROM_IIC", "switch_channel": "Datalogger-1", "addr": "0x53"}
 }

@pytest.fixture(scope="module")
def scope():
    with mock.patch.object(AD7177, '__init__', return_value=None) as mock_adc_init:
        return Scope002001A(_scope002_profile)


class TestScope002001AClass():

    def test_init(self):
        with mock.patch.object(AD7177, '__init__', return_value=None) as mock_adc_init:
            scope = Scope002001A(_scope002_profile)
            assert scope.adc_device != False
            assert scope.profile == _scope002_profile
            assert scope.datalogger_samplerate == (1000,"Hz")

    def test_adc_register_write(self,scope):
        with mock.patch.object(AD7177,"register_write",return_value=False) as mock_register_write:
            ret = scope.adc_register_write(0x00,0x23)
            assert ret == False

        with mock.patch.object(AD7177,"register_write",return_value=True) as mock_register_write:
            ret = scope.adc_register_write(0x00,0x23)
            assert ret == True

    def test_adc_register_read(self,scope):
        with mock.patch.object(AD7177,"register_read",return_value=False) as mock_register_read:
            ret = scope.adc_register_read(0x00)
            assert ret == False

        with mock.patch.object(AD7177,"register_read",return_value=0x5a) as mock_register_read:
            ret = scope.adc_register_read(0x00)
            assert ret == 0x5a


    def test_adc_samplerate_set(self,scope):
        with mock.patch.object(AD7177,"samplerate_set",return_value=False) as mock_samplerate_set:
            samplerates=[("current",(5,'Hz')),("voltage",(10,'Hz'))]
            for channel,samplerate in samplerates:
                ret = scope.adc_samplerate_set(channel,samplerate)
                assert ret == False

        with mock.patch.object(AD7177,"samplerate_set",return_value=True) as mock_samplerate_set:
            samplerates=[("current",(5,'Hz')),("voltage",(10,'Hz'))]
            for channel,samplerate in samplerates:
                ret = scope.adc_samplerate_set(channel,samplerate)
                assert ret == True

            samplerates=[("testerror",(5,'Hz')),("voltage","testerror")]
            for channel,samplerate in samplerates:
                try:
                    ret = scope.adc_samplerate_set(channel,samplerate)
                    assert False
                except ValueError:
                    assert True
                except KeyError:
                    assert True

    def test_adc_samplerate_get(self,scope):

        samplerates=[("current",(5,'Hz')),("voltage",(10,'Hz')),("current",False)]
        for channel,samplerate in samplerates: 
            with mock.patch.object(AD7177,"samplerate_get",return_value=samplerate) as mock_samplerate_get:
                ret = scope.adc_samplerate_get(channel)
                assert ret == samplerate

        try:
            ret = scope.adc_samplerate_get("testeror")
            assert False
        except ValueError:
            assert True
        except KeyError:
            assert True

    def test_board_initial(self,scope):
        return_val=[True,True,True,True,True,True,True,True,True,True]
        for i in range(0,len(return_val)):
            return_val[i] = False
            with mock.patch.object(AD7177, 'reset', return_value=return_val[0]) as mock_reset:
                with mock.patch.object(AD7177, 'single_sample_mode', return_value=return_val[1]) as mock_single_sample_mode:
                    with mock.patch.object(AD7177, 'is_comunication_ok', return_value=return_val[2]) as mock_is_comunication_ok:
                        with mock.patch.object(AD7177, 'voltage_channel_disable', return_value=return_val[3]) as mock_voltage_channel_disable:
                            with mock.patch.object(AD7177, 'setup_register_set', return_value=return_val[4]) as mock_setup_register_set:
                                with mock.patch.object(AD7177, 'samplerate_set', return_value=return_val[5])as mock_samplerate_set:
                                    with mock.patch.object(AD7177, 'mode_register_set', return_value=return_val[6]) as mock_mode_register_set:
                                        with mock.patch.object(AD7177, 'voltage_get', return_value=return_val[7]) as mock_voltage_get:
                                             with mock.patch.object(AD7177, 'ifmode_register_set', return_value=return_val[8]) as mock_ifmode_register_set:
                                                with mock.patch.object(AD7177, 'continue_mode_frame_config_set', return_value=return_val[9]) as mock_continue_mode_frame_config_set:
                                                    ret = scope.board_initial()
                                                    assert ret == False
            return_val[i] = True


        with mock.patch.object(AD7177, 'reset', return_value=True) as mock_reset:
            with mock.patch.object(AD7177, 'single_sample_mode', return_value=True) as mock_single_sample_mode:
                with mock.patch.object(AD7177, 'is_comunication_ok', return_value=True) as mock_is_comunication_ok:
                    with mock.patch.object(AD7177, 'voltage_channel_disable', return_value=True) as mock_voltage_channel_disable:
                        with mock.patch.object(AD7177, 'setup_register_set', return_value=True) as mock_setup_register_set:
                            with mock.patch.object(AD7177, 'samplerate_set', return_value=True)as mock_samplerate_set:
                                with mock.patch.object(AD7177, 'mode_register_set', return_value=True) as mock_mode_register_set:
                                    with mock.patch.object(AD7177, 'voltage_get', return_value=True) as mock_voltage_get:
                                        with mock.patch.object(AD7177, 'ifmode_register_set', return_value=True) as mock_ifmode_register_set:
                                            with mock.patch.object(AD7177, 'continue_mode_frame_config_set', return_value=True) as mock_continue_mode_frame_config_set:
                                                ret = scope.board_initial()
                                                assert ret == True