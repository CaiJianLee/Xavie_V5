import pytest
import mock
from ee.chip.cat9555 import CAT9555
from ee.overlay.i2cbus import I2cBus
from ee.common import logger

cat9555_profile={
    "bus":"i2c-0",
    "switch_channel":None,
    "addr":0x03
}

@pytest.fixture(scope="module")
def cat9555():
    with mock.patch.object(I2cBus, "__init__", return_value=None) as mock_init_ci2cbus:
        return CAT9555(cat9555_profile)



class TestCAT9555Class():
    def test_init(self,cat9555):
        with mock.patch.object(I2cBus, "__init__", return_value=None) as mock_init_ci2cbus:
            device_addrs=[0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x27,0x24]
            test_profile={    "bus":"i2c-0","switch_channel":None,"addr":0x03}
            for device_addr in device_addrs:
                test_profile["addr"]=device_addr
                cat9555 = CAT9555(test_profile)
                assert cat9555._device_addr == (device_addr&0x07|0x20)


    def test_read(self,cat9555):
        return_vals=[[0x00,0x00],[0x23,0x23],False]
        for return_val  in return_vals:
            with mock.patch.object(I2cBus, "rdwr", return_value=return_val) as mock_rdwr:
                ret = cat9555.read(0x00,2)
                assert ret == return_val

    def test_write(self,cat9555):
        return_vals=[True,False]
        for return_val  in return_vals:
            with mock.patch.object(I2cBus, "write", return_value=return_val) as mock_write_ci2cbus:
                ret = cat9555.write(0x00,[0x00,0x02])
                assert ret == return_val

    def test_write_dir_config(self,cat9555):
        return_vals=[True,False]
        for return_val  in return_vals:
            with mock.patch.object(CAT9555, "write", return_value=return_val) as mock_write:
                ret = cat9555.write_dir_config([0x00,0x02])
                assert ret == return_val

    def test_read_dir_config(self,cat9555):
        return_vals=[[0x00,0x00],[0x23,0x23],False]
        for return_val  in return_vals:
            with mock.patch.object(CAT9555, "read", return_value=return_val) as mock_read:
                ret = cat9555.read_dir_config()
                assert ret == return_val

    def test_write_outport(self,cat9555):
        return_vals=[True,False]
        for return_val  in return_vals:
            with mock.patch.object(CAT9555, "write", return_value=return_val) as mock_write:
                ret = cat9555.write_outport([0x00,0x02])
                assert ret == return_val

    def test_read_outport(self,cat9555):
        return_vals=[[0x00,0x00],[0x23,0x23],False]
        for return_val  in return_vals:
            with mock.patch.object(CAT9555, "read", return_value=return_val) as mock_read:
                ret = cat9555.read_outport()
                assert ret == return_val

    def test_write_inversion(self,cat9555):
        return_vals=[True,False]
        for return_val  in return_vals:
            with mock.patch.object(CAT9555, "write", return_value=return_val) as mock_write:
                ret = cat9555.write_inversion([0x00,0x02])
                assert ret == return_val

    def test_read_inversion(self,cat9555):
        return_vals=[[0x00,0x00],[0x23,0x23],False]
        for return_val  in return_vals:
            with mock.patch.object(CAT9555, "read", return_value=return_val) as mock_read:
                ret = cat9555.read_inversion()
                assert ret == return_val

    def test_read_inport(self,cat9555):
        return_vals=[[0x00,0x00],[0x23,0x23],False]
        for return_val  in return_vals:
            with mock.patch.object(CAT9555, "read", return_value=return_val) as mock_read:
                ret = cat9555.read_inport()
                assert ret == return_val

    def test_read_out_in_state(self,cat9555):
        dir_datas=([0x5a,0x5a],[0xff,0x00],[0x00,0xff],[0x00,0x00],[0xff,0xff],[0x5a,0x00],[0xa5,0x00])
        input_datas=([0x5a,0x5a],[0xff,0x00],[0x00,0xff],[0x00,0x00],[0xff,0xff],[0x5a,0x00],[0xa5,0x00])
        output_datas=([0x5a,0x5a],[0xff,0x00],[0x00,0xff],[0x00,0x00],[0xff,0xff],[0x5a,0x00],[0xa5,0x00])
        for dir_data in dir_datas:
            with mock.patch.object(CAT9555, "read_dir_config", return_value=dir_data) as mock_read_dir_config:
                for input_data in input_datas:
                    with mock.patch.object(CAT9555, "read_inport", return_value=input_data) as mock_read_inport:
                        for output_data in output_datas:
                            with mock.patch.object(CAT9555, "read_outport", return_value=output_data) as mock_read_outport:
                                ret = cat9555.read_out_in_state()
                                result=[0x00,0x00]
                                for i in range(0,2):
                                    result[i] = dir_data[i]&input_data[i]
                                    output_data[i] = ((~dir_data[i])&0xff)&output_data[i]
                                    result[i] |= output_data[i]
                                assert  ret == result
