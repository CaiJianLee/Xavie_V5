
import pytest
import mock
from ee.board.dmm001.dmm001001 import Dmm001001
from ee.chip.ad7175 import AD7175
import ee.overlay.extendio as ExtendIo
import ee.board.dmm001.dmm001001 as DMM001001

_dmm001001profile ={
            "partno": "Dmm-001-001",
            "id":"dmm",
            "adc": {"partno": "AD7175", "path": "AXI4_DMM_AD7175","samplerate":"5Hz","vref": "5000mV","chipnum":0},
            "io": {
                "BIT1": "bit81",
                "BIT2": "bit82",
                "BIT3": "bit83",
                "profile":{
                    "io-1": {"addr":"0x40", "switch": "back-light", "bus": "/dev/i2c-0"},
                    "bit81": {"pin": 1, "chip": "io-1",},
                    "bit82": {"pin": 2, "chip": "io-1"},
                    "bit83": {"pin": 3, "chip": "io-1"}
                }
            },
            "eeprom": {"partno": "CAT24C08", "bus": "EEPROM_IIC", "switch_channel": "DMM_1","addr": "0x51"}
 }

@pytest.fixture(scope="module")
def dmm():
    with mock.patch.object(AD7175, '__init__', return_value=None) as mock_adc_init:
        return Dmm001001(_dmm001001profile)


class TestDmm001001Class():

    def test_init(self):
        with mock.patch.object(AD7175, '__init__', return_value=None) as mock_adc_init:
            dmm = Dmm001001(_dmm001001profile)
            assert dmm.adc_device != False
            assert dmm.profile == _dmm001001profile
            assert dmm.adc_samplerate["current"] == (5, 'Hz')
            assert dmm.adc_samplerate["voltage"] == (5, 'Hz')

    def test_board_initial(self,dmm):
        return_val=[True,True,True,True,True,True,True,True,True]
        for i in range(0,len(return_val)):
            return_val[i] = False
            with mock.patch.object(AD7175, 'reset', return_value=return_val[0]) as mock_reset:
                with mock.patch.object(AD7175, 'single_sample_mode', return_value=return_val[1]) as mock_single_sample_mode:
                    with mock.patch.object(AD7175, 'is_comunication_ok', return_value=return_val[2]) as mock_is_comunication_ok:
                        with mock.patch.object(AD7175, 'voltage_channel_disable', return_value=return_val[3]) as mock_voltage_channel_disable:
                            with mock.patch.object(AD7175, 'setup_register_set', return_value=return_val[4]) as mock_setup_register_set:
                                with mock.patch.object(AD7175, 'samplerate_set', return_value=return_val[5])as mock_samplerate_set:
                                    with mock.patch.object(AD7175, 'mode_register_set', return_value=return_val[6]) as mock_mode_register_set:
                                        with mock.patch.object(AD7175, 'voltage_get', return_value=return_val[7]) as mock_voltage_get:
                                             with mock.patch.object(AD7175, 'ifmode_register_set', return_value=return_val[8]) as mock_ifmode_register_set:
                                                ret = dmm.board_initial()
                                                assert ret == False
                                                assert dmm.measure_path["channel"] == "voltage"
                                                assert dmm.measure_path["range"] == "5V"
            return_val[i] = True


            with mock.patch.object(AD7175, 'reset', return_value=True) as mock_reset:
                with mock.patch.object(AD7175, 'single_sample_mode', return_value=True) as mock_single_sample_mode:
                    with mock.patch.object(AD7175, 'is_comunication_ok', return_value=True) as mock_is_comunication_ok:
                        with mock.patch.object(AD7175, 'voltage_channel_disable', return_value=True) as mock_voltage_channel_disable:
                            with mock.patch.object(AD7175, 'setup_register_set', return_value=True) as mock_setup_register_set:
                                with mock.patch.object(AD7175, 'samplerate_set', return_value=True)as mock_samplerate_set:
                                    with mock.patch.object(AD7175, 'mode_register_set', return_value=True) as mock_mode_register_set:
                                        with mock.patch.object(AD7175, 'voltage_get', return_value=True) as mock_voltage_get:
                                            with mock.patch.object(AD7175, 'ifmode_register_set', return_value=True) as mock_ifmode_register_set:
                                                ret = dmm.board_initial()
                                                assert ret == True
                                                assert dmm.measure_path["channel"] == "voltage"
                                                assert dmm.measure_path["range"] == "5V"

    def test_board_reset(self,dmm):
        return_vals=[True,False]
        for return_val in return_vals:
            with mock.patch.object(Dmm001001, 'board_initial', return_value=return_val) as mock_board_initial:
                ret = dmm.board_reset()
                assert ret == return_val

    def test_calibration_work_mode_open(self,dmm):
        dmm.calibration_work_mode_open()
        assert dmm.cal_mode_flag == 'in'

    def test_calibration_work_mode_close(self,dmm):
        dmm.calibration_work_mode_close()
        assert dmm.cal_mode_flag == 'out'

    def test_measure_path_set(self,dmm):
        with mock.patch.object(ExtendIo, 'set', return_value=True) as mock_io_set:
            paths=[{"channel":"voltage","range":"5V"},
                            {"channel":"current","range":"100uA"},
                             {"channel":"current","range":"2mA"}
                         ]
            for path in paths:
                ret = dmm.measure_path_set(path)
                assert ret == True
                rdpath = dmm.measure_path_get()
                assert rdpath == path

            paths=[{"test_error":"voltage","range":"5V"},
                          {"channel":"voltage","range":"test_error"},
                          {"channel":"test_error","range":"100uA"},
                          {"channel":"current","test_error":"2mA"},
                          {"channel":"current","range":"test_error"},
                        ]
            default_path ={"channel":"voltage","range":"5V"}
            ret = dmm.measure_path_set(default_path)
            assert ret == True
            for path in paths:
                try:
                    ret = dmm.measure_path_set(path)
                    assert False
                except ValueError:
                    assert True
                except KeyError:
                    assert True

    def test_measure_path_record(self,dmm):
        paths=[{"channel":"voltage","range":"5V"},
                        {"channel":"current","range":"100uA"},
                        {"channel":"current","range":"2mA"}
                    ]
        for path in paths:
            ret = dmm.measure_path_record(path)
            assert ret == True
            rdpath = dmm.measure_path_get()
            assert rdpath == path

        paths=[{"test_error":"voltage","range":"5V"},
                        {"channel":"voltage","range":"test_error"},
                        {"channel":"test_error","range":"100uA"},
                        {"channel":"current","test_error":"2mA"},
                        {"channel":"current","range":"test_error"},
                    ]
        default_path ={"channel":"voltage","range":"5V"}
        ret = dmm.measure_path_record(default_path)
        assert ret == True
        for path in paths:
            try:
                ret = dmm.measure_path_record(path)
                assert False
            except ValueError:
                assert True
            except KeyError:
                assert True


    def test_measure_path_get(self,dmm):
        with mock.patch.object(ExtendIo, 'set', return_value=True) as mock_io_set:
            paths=[{"channel":"voltage","range":"5V"},
                            {"channel":"current","range":"100uA"},
                             {"channel":"current","range":"2mA"}
                         ]
            for path in paths:
                ret = dmm.measure_path_set(path)
                assert ret == True
                rdpath = dmm.measure_path_get()
                assert rdpath == path

            paths=[{"test_error":"voltage","range":"5V"},
                          {"channel":"voltage","range":"test_error"},
                          {"channel":"test_error","range":"100uA"},
                          {"channel":"current","test_error":"2mA"},
                          {"channel":"current","range":"test_error"},
                        ]
            default_path ={"channel":"voltage","range":"5V"}
            ret = dmm.measure_path_set(default_path)
            assert ret == True
            for path in paths:
                try:
                    ret = dmm.measure_path_set(path)
                    assert False
                except KeyError:
                    assert True
                except ValueError:
                    assert True
                rdpath = dmm.measure_path_get()
                assert rdpath == default_path

    def test_voltage_measure(self,dmm):

        with mock.patch.object(ExtendIo, 'set', return_value=True) as mock_io_set:
            setpath = {"channel":"voltage","range":"5V"}
            ret = dmm.measure_path_set(setpath)
            assert ret == True

        return_val = (3000,"mV")
        with mock.patch.object(AD7175, 'voltage_get', return_value =return_val) as mock_voltage_get:
                volt = dmm.voltage_measure()
                assert volt != False
                assert volt == return_val

        with mock.patch.object(AD7175, 'voltage_get', return_value=False) as mock_voltage_get:
            volt = dmm.voltage_measure()
            assert volt == False

    def test_current_measure(self,dmm):

        with mock.patch.object(ExtendIo, 'set', return_value=True) as mock_io_set:
            paths = [{"channel":"current","range":"100uA"},
                            {"channel":"current","range":"2mA"}
                          ]
            for path in paths:
                ret = dmm.measure_path_set(path)
                assert ret == True

                return_val = (3000,"mV")
                with mock.patch.object(AD7175, 'voltage_get', return_value=return_val) as mock_voltage_get:
                        current = dmm.current_measure()
                        assert current != False
                        sampling_resistor = DMM001001._dmm_board_description["channel"]["current"]["range"][path["range"]]["sample_resistor"]
                        gain = DMM001001._dmm_board_description["channel"]["current"]["range"][path["range"]]["gain"]
                        assert current == (3000/(gain*sampling_resistor[0]),"mA")

                with mock.patch.object(AD7175, 'voltage_get', return_value=False) as mock_voltage_get:
                    current = dmm.current_measure()
                    assert current == False

    def test_adc_register_write(self,dmm):
        with mock.patch.object(AD7175,"register_write",return_value=False) as mock_register_write:
            ret = dmm.adc_register_write(0x00,0x23)
            assert ret == False

        with mock.patch.object(AD7175,"register_write",return_value=True) as mock_register_write:
            ret = dmm.adc_register_write(0x00,0x23)
            assert ret == True

    def test_adc_register_read(self,dmm):
        with mock.patch.object(AD7175,"register_read",return_value=False) as mock_register_read:
            ret = dmm.adc_register_read(0x00)
            assert ret == False

        with mock.patch.object(AD7175,"register_read",return_value=0x5a) as mock_register_read:
            ret = dmm.adc_register_read(0x00)
            assert ret == 0x5a


    def test_adc_samplerate_set(self,dmm):
        with mock.patch.object(AD7175,"samplerate_set",return_value=False) as mock_samplerate_set:
            samplerates=[("current",(5,'Hz')),("voltage",(10,'Hz'))]
            for channel,samplerate in samplerates:
                ret = dmm.adc_samplerate_set(channel,samplerate)
                assert ret == False

        with mock.patch.object(AD7175,"samplerate_set",return_value=True) as mock_samplerate_set:
            samplerates=[("current",(5,'Hz')),("voltage",(10,'Hz'))]
            for channel,samplerate in samplerates:
                ret = dmm.adc_samplerate_set(channel,samplerate)
                assert ret == True

            samplerates=[("testerror",(5,'Hz')),("voltage","testerror")]
            for channel,samplerate in samplerates:
                try:
                    ret = dmm.adc_samplerate_set(channel,samplerate)
                    assert False
                except ValueError:
                    assert True
                except KeyError:
                    assert True

    def test_adc_samplerate_get(self,dmm):

        samplerates=[("current",(5,'Hz')),("voltage",(10,'Hz')),("current",False)]
        for channel,samplerate in samplerates: 
            with mock.patch.object(AD7175,"samplerate_get",return_value=samplerate) as mock_samplerate_get:
                ret = dmm.adc_samplerate_get(channel)
                assert ret == samplerate

        try:
            ret = dmm.adc_samplerate_get("testeror")
            assert False
        except ValueError:
            assert True
        except KeyError:
            assert True



# if __name__ =='__main__': 
#     pytest.main()
