import pytest
import mock
from ee.chip.tca9548 import TCA9548
import ee.overlay.i2cbus as I2CBus
from ee.bus.ci2c import CI2cBus
from ee.common import logger


@pytest.fixture(scope="module")
def tca9548():
    with mock.patch.object(CI2cBus, "__init__", return_value=None) as mock_init_ci2cbus:
        return TCA9548("i2c-0",0x01)


class TestTCA9548Class():
    def test_init(self):
        i2c_name="i2c-0"
        with mock.patch.object( I2CBus, 'get_bus', return_value=i2c_name) as mock_get_bus:
            device_addrs=[0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x27,0x24]
            for device_addr in device_addrs:
                tca9548 = TCA9548(i2c_name,device_addr)
                assert tca9548._device_addr == (device_addr&0x07|0x70)

    def test_select_channel(self,tca9548):

        return_vals=[True,False]
        test_datas=[0,1,2,3,4,5,6,7]
        test_error_datas=[6.3, -1, -1.0,0.8,8,8.7,7.1]
        for return_val in return_vals:
            with mock.patch.object(CI2cBus, "write", return_value=return_val) as mock_write_ci2cbus:
                for channel in test_datas:
                    ret = tca9548.select_channel(channel)
                    assert ret == return_val

                try:
                    for channel in test_error_datas:
                        ret = tca9548.select_channel(channel)
                        assert False
                except ValueError:
                        assert True

    def test_close_channel(self,tca9548):
        return_vals=[True,False]
        for return_val in return_vals:
            with mock.patch.object(CI2cBus, "write", return_value=return_val) as mock_write_ci2cbus:
                ret = tca9548.close_channel()
                assert ret == return_val