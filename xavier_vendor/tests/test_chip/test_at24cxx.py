import pytest
import mock
from ee.chip.at24cxx import AT24Cxx
import ee.overlay.i2cbus as I2CBus
from ee.bus.ci2c import CI2cBus

global chip_args
#type,chip size,page size,memory address max byte size, device addr mask
chip_args=[("at01",128,8,1,0x00),
                    ("at02",256,8,1,0x00),
                    ("at04",512,16,1,0x01),
                    ("at08",1024,16,1,0x03),
                    ("at16",2048,16,1,0x07),
                    ("at32",4096,32,2,0x00),
                    ("at64",8*1024,32,2,0x00),
                    ("at128",16*1024,64,2,0x04),
                    ("at256",32*1024,64,2,0x04),
                    ("at512",64*1024,128,2,0x04)]

@pytest.fixture(scope="module")
def at24cxx():
    with mock.patch.object(CI2cBus, "__init__", return_value=None) as mock_init_ci2cbus:
        return AT24Cxx("i2c-0",0x04,"at08")

class TestAT24CxxClass():
    def test_init(self):
        i2c_name="i2c-0"
        with mock.patch.object( I2CBus, 'get_bus', return_value=i2c_name) as mock_get_bus:
            global chip_args
            device_addrs=[0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07]
            for chip_type,chip_size,page_size,memory_addr_size,mask in chip_args:
                for device_addr in device_addrs:
                    at24cxx = AT24Cxx(i2c_name,device_addr,chip_type)
                    assert at24cxx._device_addr == ((device_addr&(~mask))|0x50)
                    assert at24cxx._page_size == page_size
                    assert at24cxx._chip_size == chip_size
                    assert at24cxx._memory_address_size == memory_addr_size

    def test___memory_address_to_byte_list(self):
        i2c_name="i2c-0"
        with mock.patch.object( I2CBus, 'get_bus', return_value=i2c_name) as mock_get_bus:
            memory_addrs=[{"addr":0x00,"list":(0x00,0x00)},{"addr":0x5a,"list":(0x00,0x5a)},{"addr":0x1f5a,"list":(0x1f,0x5a)}]
            global chip_args
            for chip_type,chip_size,page_size,memory_addr_size,mask in chip_args:
                for memory_addr in memory_addrs:
                    at24cxx = AT24Cxx(i2c_name,0x07,chip_type)
                    addr_list = at24cxx._memory_address_to_byte_list(memory_addr["addr"])
                    assert len(addr_list) == at24cxx._memory_address_size
                    if 1 == at24cxx._memory_address_size:
                        assert addr_list[0] == memory_addr["list"][1]
                    else:
                        for i in range(0,at24cxx._memory_address_size):
                            assert addr_list[i] == memory_addr["list"][i]

    def test_read(self):
        global chip_args
        return_datas=[0x00,0x5a]
        i2c_name="i2c-0"
        with mock.patch.object(CI2cBus, "__init__", return_value=None) as mock_init_ci2cbus:
            for chip_type,chip_size,page_size,memory_addr_size,mask in chip_args:
                at24cxx = AT24Cxx(i2c_name,0x07,chip_type)
                with mock.patch.object(CI2cBus,"rdwr",return_value=return_datas) as mock_i2c_rdwr:
                    data_list = at24cxx.read(0x00,2)
                    for i in range(0,len(return_datas)):
                        assert data_list[i] == return_datas[i]

                with mock.patch.object(CI2cBus,"rdwr",return_value=False) as mock_i2c_rdwr:
                        data_list = at24cxx.read(0x00,2)
                        assert data_list == False

    def test_write(self):
        global chip_args
        i2c_name="i2c-0"
        with mock.patch.object(CI2cBus, "__init__", return_value=None) as mock_init_ci2cbus:
            for chip_type,chip_size,page_size,memory_addr_size,mask in chip_args:
                at24cxx = AT24Cxx(i2c_name,0x07,chip_type)
                with mock.patch.object(CI2cBus,"write",return_value=True) as mock_i2c_rdwr:
                    ret = at24cxx.write(0x56,[0x00,0x03])
                    assert ret == True

                with mock.patch.object(CI2cBus,"write",return_value=False) as mock_i2c_rdwr:
                        ret = at24cxx.write(0x56,[0x00,0x03])
                        assert ret == False