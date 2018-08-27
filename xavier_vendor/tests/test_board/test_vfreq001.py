import pytest
import mock
from ee.board.vfreq001.vfreq001 import Vfreq001
from ee.profile import profile
from ee.ipcore.axi4_signal_meter import Axi4SignalMeter
from ee.board.ins001.vvo001 import Vvo001

_vfreq001_profile ={
    "name": "freq",
    "partno": "Vfreq-001-001",
    "path": "/dev/AXI4_FREQ",
    "ipcore": "Axi4SignalMeter",
    "samplerate":"1000KHz",
    "vo": {"name": "voltage_output", "channel": "vo1"}
 }


@pytest.fixture(scope="module")
def vfreq():
    with mock.patch.object(Axi4SignalMeter, '__init__', return_value=None) as mock_signal_meter:
        with mock.patch.object(profile, 'get_class', return_value=None) as mock_get_class:
            return Vfreq001(_vfreq001_profile)


class TestVfreq001Class():

    def test_init(self):
        with mock.patch.object(Axi4SignalMeter, '__init__', return_value=None) as mock_signal_meter:
            with mock.patch.object(profile, 'get_class', return_value=None) as mock_get_class:
                vfreq = Vfreq001(_vfreq001_profile)
                assert vfreq.samplerate  == (1000,'KHz')

    def test_board_initial(self,vfreq):
        ret = vfreq.board_initial()
        assert ret == True

    def test_frequency_measure(self,vfreq):

        vref = (200,'mV')
        result = {"freq":(1000,'Hz'), 
                        "duty":(50,'%'),
                        }
        with mock.patch.object(Vvo001, 'voltage_output', return_value=True) as mock_voltage_output:
            with mock.patch.object(Axi4SignalMeter, 'enable', return_value=None) as mock_signal_meter_enable:
                with mock.patch.object(Axi4SignalMeter, 'measure_start', return_value=True) as mock_signal_meter_measure_start:
                    with mock.patch.object(Axi4SignalMeter, 'frequency_measure', return_value=result['freq']) as mock_signal_meter_frequency_measure:
                        with mock.patch.object(Axi4SignalMeter, 'duty_measure', return_value=result['duty']) as mock_signal_meter_duty_measure:
                            ret = vfreq.frequency_measure(vref,(300,'ms'))
                            assert ret == result
