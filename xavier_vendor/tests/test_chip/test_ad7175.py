import pytest
import mock
from ee.chip.ad7175 import AD7175
from ee.ipcore.axi4_ad717x import Axi4Ad717x


@pytest.fixture(scope="module")
def ad7175():
    with mock.patch.object(Axi4Ad717x, "__init__", return_value=None) as mock_init:
        return AD7175("/dev/AXI4_DMM_AD7175",(5000,"mV"))


class TestAD7175Class():

    def test_init(self):
        with mock.patch.object(Axi4Ad717x, "__init__", return_value=None) as mock_init:
            vref = (5000,"mV")
            ad7175 =  AD7175("/dev/AXI4_DMM_AD7175",vref)
            assert ad7175.vref == vref

    def test_single_sample_mode(self,ad7175):
        return_vals=[True,False]
        for return_val in return_vals:
            with mock.patch.object(Axi4Ad717x, "single_sample_mode", return_value=return_val) as mock_single_sample_mode:
                ret = ad7175.single_sample_mode()
                assert ret==return_val

    def test_register_read(self,ad7175):
        return_vals=[0x07,False]
        for return_val in return_vals:
            with mock.patch.object(Axi4Ad717x, "register_read", return_value=return_val) as mock_register_read:
                ret = ad7175.register_read(0x00)
                assert ret==return_val

    def test_register_write(self,ad7175):
        return_vals=[True,False]
        for return_val in return_vals:
            with mock.patch.object(Axi4Ad717x, "register_write", return_value=return_val) as mock_register_write:
                ret = ad7175.register_write(0x00,0x88)
                assert ret==return_val

    def test_voltage_channel_enable(self,ad7175):
        return_vals=[True,False]
        args=[("chan0",{"P":"AIN0","N":"AIN1"}),
                   ("chan1", {"P":"AIN2","N":"AIN3"}),
                   ("chan2", {"P":"AIN2","N":"AIN3"}),
                   ("chan3", {"P":"AIN2","N":"AIN3"}),
                   ("chan3", {"P":"Temp+","N":"Temp-"}),
                   ("chan3", {"P":"AVDD1","N":"AVSS"}),
                   ("chan3", {"P":"REF+","N":"REF-"}),
                  ]
        for return_val in return_vals:
            for channel,config in args:
                with mock.patch.object(AD7175, "register_write", return_value=return_val) as mock_register_write:
                    ret = ad7175.voltage_channel_enable(channel,config)
                    assert ret==return_val

        args=[("test_error",{"P":"AIN0","N":"AIN1"}),
                   ("chan1", {"test_error":"AIN2","N":"AIN3"}),
                   ("chan2", {"P":"AIN2","test_error":"AIN3"}),
                   ("chan3", {"P":"test_error","N":"AIN3"}),
                   ("chan3", {"P":"Temp+","N":"test_error"}),
                   ("chan3", "test_error"),
                  ]
        for channel,config in args:
            with mock.patch.object(AD7175, "register_write", return_value=True) as mock_register_write:
                try:
                    ret = ad7175.voltage_channel_enable(channel,config)
                    assert False
                except KeyError:
                    assert True
                except TypeError:
                    assert True

    def test_voltage_single_channel_select(self,ad7175):
        return_vals=[True,False]
        args=[("chan0",{"P":"AIN0","N":"AIN1"}),
                   ("chan1", {"P":"AIN2","N":"AIN3"}),
                   ("chan2", {"P":"AIN2","N":"AIN3"}),
                   ("chan3", {"P":"AIN2","N":"AIN3"}),
                   ("chan3", {"P":"Temp+","N":"Temp-"}),
                   ("chan3", {"P":"AVDD1","N":"AVSS"}),
                   ("chan3", {"P":"REF+","N":"REF-"}),
                  ]
        for return_val in return_vals:
            for channel,config in args:
                with mock.patch.object(AD7175, "register_write", return_value=return_val) as mock_register_write:
                    ret = ad7175.voltage_single_channel_select(channel,config)
                    assert ret==return_val

        args=[("test_error",{"P":"AIN0","N":"AIN1"}),
                   ("chan1", {"test_error":"AIN2","N":"AIN3"}),
                   ("chan2", {"P":"AIN2","test_error":"AIN3"}),
                   ("chan3", {"P":"test_error","N":"AIN3"}),
                   ("chan3", {"P":"Temp+","N":"test_error"}),
                   ("chan3", "test_error"),
                  ]
        for channel,config in args:
            with mock.patch.object(AD7175, "register_write", return_value=True) as mock_register_write:
                try:
                    ret = ad7175.voltage_single_channel_select(channel,config)
                    assert False
                except KeyError:
                    assert True
                except TypeError:
                    assert True

    def test_voltage_get(self,ad7175):
        return_vals=[(False,(0x00,0x5678),(3000,"mV"),False),
                                (True,False,(3000,"mV"),False),
                                (True,(0x00,0x5678),False,False),
                                ]
        for return_val in return_vals:
            with mock.patch.object(AD7175, "voltage_single_channel_select", return_value=return_val[0]) as mock_voltage_single_channel_select:
                with mock.patch.object(Axi4Ad717x, "single_sample_code_get", return_value=return_val[1]) as mock_single_sample_code_get:
                    with mock.patch.object(Axi4Ad717x, "code_2_mvolt", return_value=return_val[2]) as mock_code_2_mvolt:
                        ret = ad7175.voltage_get("chan0",{"P":"AIN0","N":"AIN1"})
                        assert ret==return_val[3]

        args=[((0x00,0x5678),"chan0",{"P":"AIN0","N":"AIN1"}),
                    ((0x01,0x5678),"chan1",{"P":"AIN0","N":"AIN1"}),
                    ((0x02,0x5678),"chan2",{"P":"AIN0","N":"AIN1"}),
                    ((0x03,0x5678),"chan3",{"P":"AIN0","N":"AIN1"}),
                    ]
        for arg in args:
            with mock.patch.object(AD7175, "voltage_single_channel_select", return_value=True) as mock_voltage_single_channel_select:
                with mock.patch.object(Axi4Ad717x, "single_sample_code_get", return_value=arg[0]) as mock_single_sample_code_get:
                    with mock.patch.object(Axi4Ad717x, "code_2_mvolt", return_value=(3000,"mV")) as mock_code_2_mvolt:
                        ret = ad7175.voltage_get(arg[1],arg[2])
                        assert ret==(3000,"mV")

        args=[(False,"chan0",{"P":"AIN0","N":"AIN1"}),
                    ]
        for code,channel,config in args:
            with mock.patch.object(AD7175, "voltage_single_channel_select", return_value=True) as mock_voltage_single_channel_select:
                with mock.patch.object(Axi4Ad717x, "single_sample_code_get", return_value=code) as mock_single_sample_code_get:
                    with mock.patch.object(Axi4Ad717x, "code_2_mvolt", return_value=(3000,"mV")) as mock_code_2_mvolt:
                        ret = ad7175.voltage_get(channel,config)
                        assert ret == False


    def test_is_comunication_ok(self,ad7175):
        args=[(0xffff,False),
                    (0x0cde,True),
                    (0x0000,False),
                    (0x0FF0,False),
                    (False,False)
                    ]
        for read_return,result_return in args:
            with mock.patch.object(AD7175, "register_read", return_value=read_return) as mock_register_read:
                ret = ad7175.is_comunication_ok()
                assert ret == result_return
    def test_ifmode_register_set(self,ad7175):
        test_args=[
                    ("enable","24bits",True),
                    ("disable","24bits",True),
                    ("enable","16bits",True),
                    ("disable","16bits",False)
                ]
        for data_stat_channel_flag, data_bits,result in test_args:
            with mock.patch.object(AD7175, "register_write", return_value=result) as mock_register_write:
                ret = ad7175.ifmode_register_set(data_stat_channel_flag,data_bits)
                assert ret == result

        test_args=[
                    ("test_error","24bits",True),
                    ("disable","test_eeror",True),
                ]
        for data_stat_channel_flag, data_bits,result in test_args:
            with mock.patch.object(AD7175, "register_write", return_value=result) as mock_register_write:
                try:
                    ret = ad7175.ifmode_register_set(data_stat_channel_flag,data_bits)
                    assert False
                except KeyError:
                    assert True

    def test_mode_register_set(self,ad7175):
        test_args=[("internal",True),
                            ("clock",True),
                            ("crystal",True),
                            ("internal",False),
                            ("clock",False),
                            ("crystal",False)
                            ]
        for clock_source,result in test_args:
            with mock.patch.object(AD7175, "register_write", return_value=result) as mock_register_write:
                ret = ad7175.mode_register_set(clock_source)
                assert ret == result

        with mock.patch.object(AD7175, "register_write", return_value=True) as mock_register_write:
            try:
                ret = ad7175.mode_register_set("test_error")
                assert False
            except KeyError:
                assert True

    def test_setup_register_set(self,ad7175):
        test_args=[("chan0","bipolar","extern","enable"),
                            ("chan1","unipolar","internal","disable"),
                            ("chan2","bipolar","extern","enable"),
                           ("chan3","bipolar","AVDD-AVSS","enable"),
                            ]
        return_vals=[True,False]
        for return_val in return_vals:
            for channel,code_polar,reference,buffer_flag in test_args:
                with mock.patch.object(AD7175, "register_write", return_value=return_val) as mock_register_write:
                    ret = ad7175.setup_register_set(channel,code_polar,reference,buffer_flag )
                    assert ret == return_val

        test_args=[("test_error","bipolar","extern","enable"),
                            ("chan1","test_error","internal","disable"),
                            ("chan2","bipolar","test_error","enable"),
                           ("chan3","bipolar","AVDD-AVSS","test_error"),
                            ]
        for channel,code_polar,reference,buffer_flag in test_args:
                with mock.patch.object(AD7175, "register_write", return_value=True) as mock_register_write:
                    try:
                        ret = ad7175.setup_register_set(channel,code_polar,reference,buffer_flag )
                        assert False
                    except KeyError:
                        assert True

    def test_samplerate_set(self,ad7175):
        test_args=[("chan0",(5,"Hz")),
                            ("chan1",(10,"Hz")),
                            ("chan2",(11,"Hz")),
                           ("chan3",(1000,"Hz")),
                            ]
        return_vals=[(False,True,False),
                                (0x100,False,False),
                                (0x500,True,True)
                                ]

        for read_return,write_return,result_return in return_vals:
            for channel,samplerate in test_args:
                with mock.patch.object(AD7175, "register_read", return_value=read_return) as mock_register_read:
                    with mock.patch.object(AD7175, "register_write", return_value=write_return) as mock_register_write:
                        ret = ad7175.samplerate_set(channel,samplerate)
                        assert ret == result_return

        test_args=[("test_error",(5,"Hz")),
                            ("chan1","test_error"),
                            ("chan1",("77","Hz")),
                            ("chan1",("77","Hz",3)),
                            ]
        for channel,samplerate in test_args:
            with mock.patch.object(AD7175, "register_read", return_value=0x500) as mock_register_read:
                with mock.patch.object(AD7175, "register_write", return_value=True) as mock_register_write:
                    try:
                        ret = ad7175.samplerate_set(channel,samplerate)
                        assert False
                    except KeyError:
                        assert True
                    except TypeError:
                        assert True
                    except ValueError:
                        assert True
    def test_samplerate_get(self,ad7175):

        test_args=[("chan0",0x14,(5,'Hz')),
                            ("chan1",0x01,(125000,'Hz')),
                            ("chan2",0x01,(125000,'Hz')),
                            ("chan3",0x01,(125000,'Hz')),
                            ("chan3",False,False),
                            ]
        for channel,return_val,result in test_args:
            with mock.patch.object(AD7175, "register_read", return_value=return_val) as mock_register_read:
                ret = ad7175.samplerate_get(channel)
                assert ret == result

        test_args=[("testerror",0x14,(5,'Hz')),
                            ]
        for channel,return_val,result in test_args:
            with mock.patch.object(AD7175, "register_read", return_value=return_val) as mock_register_read:
                try:
                    ret = ad7175.samplerate_get(channel)
                except KeyError:
                    assert True

    def test_continue_mode_frame_config_set(self,ad7175):
        test_args=[(0,(5,'Hz'),True),
                    (0,(5,'Hz'),False),
                    ]
        for channel,samplerate,result in test_args:
            with mock.patch.object(Axi4Ad717x, "frame_channel_and_samplerate_set", return_value=result) as mock_frame_channel_and_samplerate_set:
                ret = ad7175.continue_mode_frame_config_set(channel,samplerate)
                assert ret == result

    def test_continue_sample_mode(self,ad7175):
        test_args=[True,False]
        for result in test_args:
            with mock.patch.object(Axi4Ad717x, "continue_sample_mode", return_value=result) as mock_continue_sample_mode:
                ret = ad7175.continue_sample_mode()
                assert ret == result


    def test_continue_mode_codes_get(self,ad7175):
        test_args=[(2,(0x77,0x88)),
                            (2,False),
                        ]
        for count,result in test_args:
            with mock.patch.object(Axi4Ad717x, "data_analysis", return_value=result) as mock_data_analysis:
                ret = ad7175.continue_mode_codes_get(count)
                assert ret == result