import pytest
import mock
from ee.profile import profile
from ee.chip.ad5667 import AD5667
from ee.board.ins001.vvo001 import Vvo001

_vvo001_profile ={
    "name": "voltage_ouput",
    "dac1": {"name": "psu_DAC_1",  "channel": ["vo1", "vo2"]},
    "dac2": {"name": "psu_DAC_2", "channel": ["vo3", "vo4"]},
    "dac3": {"name": "psu_DAC_3",  "channel": ["vo5", "vo6"]},
}

_ad5667_profile={
    "bus":"i2c-1",
    "addr":0x00,
    "vref":"500mV",
}
ad5667 = AD5667(_ad5667_profile)

@pytest.fixture(scope="module")
def vvo():
    with mock.patch.object(profile, 'get_class', return_value=ad5667) as mock_get_class:
        return Vvo001(_vvo001_profile)



class TestVvo001Class():

    def test_init(self,vvo):
        assert vvo.dac_devices["dac1"] == ad5667
        assert vvo.dac_devices["dac2"] == ad5667
        assert vvo.dac_devices["dac3"] == ad5667
'''
    def test_board_initial(self,vvo):
        return_results=[True,False]
        for result in return_results:
            with mock.patch.object(Vvo001, 'voltage_output', return_value=result) as mock_ad5667:
                ret = vvo.board_initial()
                assert ret == result

    def test_voltage_output(self,vvo):
        test_args=[
                ('vo1',(200,'mV'),True),
                ('vo2',(200,'mV'),True),
                ('vo3',(200,'mV'),True),
                ('vo4',(200,'mV'),True),
                ('vo1',(200,'mV'),False),
                ('vo2',(200,'mV'),False),
                ('vo3',(200,'mV'),False),
                ('vo4',(200,'mV'),False),
            ]
        for channel,volt,return_result in test_args:
            with mock.patch.object(AD5667, 'voltage_output', return_value=return_result) as mock_ad5667_voltage_output:
                ret = vvo.voltage_output(channel,volt)
                assert ret == return_result

        test_args=[
                ('test_error',(200,'mV'),True),
                ('vo1',"test_error",True),
            ]
        for channel,volt,return_result in test_args:
            with mock.patch.object(AD5667, 'voltage_output', return_value=return_result) as mock_ad5667_voltage_output:
                try:
                    ret = vvo.voltage_output(channel,volt)
                    assert False
                except ValueError:
                    assert True
                except TypeError:
                    assert True

    def test_calibration_work_mode_open(self,vvo):
        vvo.calibration_work_mode_open()
        assert vvo.cal_mode_flag == 'in'

    def test_calibration_work_mode_close(self,vvo):
        vvo.calibration_work_mode_close()
        assert vvo.cal_mode_flag == 'out'
'''