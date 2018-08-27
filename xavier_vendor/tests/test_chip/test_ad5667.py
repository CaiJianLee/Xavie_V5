import pytest
import mock
from ee.chip.ad5667 import AD5667
import ee.overlay.i2cbus as I2cBus
from ee.common import utility

_ad5667_profile={
    "bus":"i2c-0",
    "addr":0x01,
    "vref":"2500.0mV",
}

@pytest.fixture(scope="module")
def ad5667():
    with mock.patch.object(I2cBus, "__init__", return_value=None) as mock_init_I2cBus:
        return AD5667(_ad5667_profile)

class TestAD5667Class():
        def test_init(self):
            with mock.patch.object( I2cBus, '__init__', return_value=None) as mock_get_bus:
                ad5667 = AD5667(_ad5667_profile)
                assert ad5667._device_addr == _ad5667_profile["addr"]|0x0c
                assert ad5667._vref ==utility.string_convert_value(_ad5667_profile["vref"])

        def test_read(self,ad5667):
            result=[0x00,0x01,0x07]
            with mock.patch.object( I2cBus, 'read', return_value=result) as mock_i2c_read:
                ret = ad5667._read()
                assert ret == result

        def test_write(self,ad5667):
            results=[True,False]
            for result in results:
                with mock.patch.object( I2cBus, 'write', return_value=result) as mock_i2c_write:
                    ret = ad5667._write(0x00,0x01,0x07)
                    assert ret == result

        def test__volt_to_code(self,ad5667):
            test_args=[((200,'mV'),0x147a),((-24,'mV'),0x00),((ad5667._vref[0]+100,'mV'),0xffff)]
            for volt,return_code in test_args:
                code = ad5667._volt_to_code(volt)
                assert return_code == code


        def test_voltage_output(self,ad5667):
            results=[True,False]
            channels=["A","B","All"]
            for result in results:
                with mock.patch.object( I2cBus, 'write', return_value=result) as mock_i2c_write:
                    for channel in channels:
                        ret = ad5667.voltage_output(channel,(200,'mV'))
                        assert ret == result
            with mock.patch.object( I2cBus, 'write', return_value=True) as mock_i2c_write:
                    try:
                        ret = ad5667.voltage_output("test_error",(200,'mV'))
                        assert False
                    except KeyError:
                        assert True

        def test_reset(self,ad5667):
            results=[True,False]
            for result in results:
                with mock.patch.object( I2cBus, 'write', return_value=result) as mock_i2c_write:
                    ret = ad5667.reset()
                    assert ret == result

        def test_work_mode_select(self,ad5667):
            results=[True,False]
            test_args=[
                            ("A","normal"),
                            ("B","1Kohm_GND"),
                            ("All","100Kohm_GND"),
                             ("All","high-Z")
                            ]
            for result in results:
                with mock.patch.object( I2cBus, 'write', return_value=result) as mock_i2c_write:
                    for channel,mode in test_args:
                        ret = ad5667.work_mode_select(channel,mode)
                        assert ret == result

        def test_ldac_pin_invalid_set(self,ad5667):
            results=[True,False]
            for result in results:
                with mock.patch.object( I2cBus, 'write', return_value=result) as mock_i2c_write:
                    ret = ad5667.ldac_pin_invalid_set()
                    assert ret == result

        def ldac_pin_enable_set(self,ad5667):
            results=[True,False]
            for result in results:
                with mock.patch.object( I2cBus, 'write', return_value=result) as mock_i2c_write:
                    ret = ad5667.ldac_pin_enable_set()
                    assert ret == result

        def test_initial(self,ad5667):
            results=[True,False]
            test_args=["internal","extern"]
            for result in results:
                with mock.patch.object( I2cBus, 'write', return_value=result) as mock_i2c_write:
                    for reference_mode in test_args:
                        ret = ad5667.initial(reference_mode)
                        assert ret == result
