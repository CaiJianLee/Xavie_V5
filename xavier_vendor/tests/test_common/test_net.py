__author__ = 'zhenhua'

import mock
import pytest
import os

from ee.common.net import *

@pytest.fixture    
def use_network_information():
    profile = {}
    profile["network_default_mode"]= {'mode': 'default', \
                    'default':      {'ip': '169.254.1.32', 'mac': '02:0a:35:00:01:4', 'mask': '255.255.255.0', 'gateway': '169.254.1.1'}, \
                    'PowerOn':  {'ip': '169.254.1.30', 'mac': '02:0a:35:00:01:3', 'mask': '255.255.255.0', 'gateway': '169.254.1.1'}, \
                    'user':          {'ip': '169.254.1.31', 'mac': '02:0a:35:00:01:4', 'mask': '255.255.255.0', 'gateway': '169.254.1.1'}}
    profile["network_user_mode"]= {'mode': 'default', \
                    'default':      {'ip': '192.168.99.40', 'mac': '02:0a:35:00:01:4', 'mask': '255.255.255.0', 'gateway': '192.168.99.1'}, \
                    'PowerOn':  {'ip': '192.168.99.30', 'mac': '02:0a:35:00:01:03', 'mask': '255.255.255.0', 'gateway': '192.168.99.1'}, \
                    'user':          {'ip': '192.168.99.4', 'mac': '02:0a:35:00:01:4', 'mask': '255.255.255.0', 'gateway': '192.168.99.1'}}
    profile["network_PowerOn_mode"]= {'mode': 'default', \
                    'default':      {'ip': '192.168.99.40', 'mac': '02:0a:35:00:01:4', 'mask': '255.255.255.0', 'gateway': '192.168.99.1'}, \
                    'PowerOn':  {'ip': '192.168.99.30', 'mac': '02:0a:35:00:01:03', 'mask': '255.255.255.0', 'gateway': '192.168.99.1'}, \
                    'user':          {'ip': '', 'mac': '', 'mask': '', 'gateway': ''}}
    return profile

def test_network_config():
    with mock.patch('ee.common.net.write_network_information') as mock_write_network_information:
        netconfig = {"start_ip": "192.168.99.11",\
                            "mask": "255.255.255.0",\
                            "exceptional_ip": "192.168.99.10"}
        mock_write_network_information_result = mock.Mock()
        network_config(netconfig)
        mock_write_network_information.assert_any_call("PowerOn:ip", "192.168.99.10")
        mock_write_network_information.assert_any_call("PowerOn:gateway", "192.168.99.1")

        netconfig = {"mask": "255.255.255.0",\
                            "exceptional_ip": "169.254.1.30"}
        network_config(netconfig)
        mock_write_network_information.assert_any_call("PowerOn:ip", "169.254.1.30")
        mock_write_network_information.assert_any_call("PowerOn:gateway", "169.254.1.1")
        assert mock_write_network_information.call_count == 4

        mock_write_network_information.reset_mock()
        netconfig = {}
        network_config(netconfig)
        assert mock_write_network_information.call_count == 0


def test_write_network_information(use_network_information):
    with mock.patch('ee.common.utility.get_config_path',return_value = "/opt/seeing/config") as mock_get_config_path:
        with mock.patch('ee.common.net.read_network_information') as mock_read_network_information:
            mock_read_network_information.return_value = use_network_information["network_user_mode"]
            write_network_information("net", "user")
            write_network_information("PowerOn:ip", "169.254.1.30")
            write_network_information("PowerOn:mac", "02:0a:35:00:01:04")
            write_network_information("PowerOn:mask", "255.255.255.0")
            write_network_information("PowerOn:gateway", "169.254.1.1")

            write_network_information("default:ip", "169.254.1.30")
            write_network_information("default:mac", "02:0a:35:00:01:04")
            write_network_information("default:mask", "255.255.255.0")
            write_network_information("default:gateway", "169.254.1.1")

            write_network_information("user:ip", "169.254.1.30")
            write_network_information("user:mac", "02:0a:35:00:01:04")
            write_network_information("user:mask", "255.255.255.0")
            write_network_information("user:gateway", "169.254.1.1")


def test_set_default_network(use_network_information):
    with mock.patch('ee.common.net.read_network_information') as mock_read_network_information:
        mock_read_network_information.return_value = use_network_information["network_user_mode"]
        with mock.patch('ee.common.net.__set_mac', return_value = True) as mock_set_mac:
            with mock.patch('ee.common.net.__set_ip', return_value = True) as mock_set_ip:
                with mock.patch('ee.common.net.__set_mask', return_value = True) as mock_set_mask:
                    with mock.patch('ee.common.net.__set_gateway', return_value = True) as mock_set_gateway:
                        assert True == set_default_network()
                    assert False == set_default_network()
                assert False == set_default_network()
            assert False == set_default_network()

        with mock.patch('ee.common.net.__set_mac', return_value = False) as mock_set_mac:
            assert False == set_default_network()

        with mock.patch('ee.common.net.__set_ip', return_value = False) as mock_set_ip:
            assert False == set_default_network()

        with mock.patch('ee.common.net.__set_mask', return_value = False) as mock_set_mask:
            assert False == set_default_network()

        with mock.patch('ee.common.net.__set_gateway', return_value = False) as mock_set_gateway:
            assert False == set_default_network()

def test_set_user_network(use_network_information):
    with mock.patch('ee.common.net.read_network_information') as mock_read_network_information:
        mock_read_network_information.return_value = use_network_information["network_user_mode"]
        with mock.patch('ee.common.net.__set_mac', return_value = True) as mock_set_mac:
            with mock.patch('ee.common.net.__set_ip', return_value = True) as mock_set_ip:
                with mock.patch('ee.common.net.__set_mask', return_value = True) as mock_set_mask:
                    with mock.patch('ee.common.net.__set_gateway', return_value = True) as mock_set_gateway:
                        assert True == set_user_network()
                    assert False == set_user_network()
                assert False == set_user_network()
            assert False == set_user_network()

        with mock.patch('ee.common.net.__set_mac', return_value = False) as mock_set_mac:
            assert False == set_user_network()

        with mock.patch('ee.common.net.__set_ip', return_value = False) as mock_set_ip:
            assert False == set_user_network()

        with mock.patch('ee.common.net.__set_mask', return_value = False) as mock_set_mask:
            assert False == set_user_network()

        with mock.patch('ee.common.net.__set_gateway', return_value = False) as mock_set_gateway:
            assert False == set_user_network()

def test_set_network():
    with mock.patch('ee.common.utility.get_config_path',return_value = "/opt/seeing/config") as mock_get_config_path:
        assert False == set_network()


def test_set_network_information(use_network_information):
    with mock.patch('ee.common.net.set_default_network') as mock_set_default_network:
        with mock.patch('ee.common.net.set_user_network') as mock_set_user_network:
            with mock.patch('ee.common.net.write_network_information', return_value = None) as mock_write_network_information:
                with mock.patch('ee.common.net.read_network_information') as mock_read_network_information:
                    mock_read_network_information.return_value = use_network_information["network_user_mode"]
                    assert False == set_network_information("ne", "default")

                    mock_set_default_network.return_value = True
                    assert True == set_network_information("mode", "default")

                    mock_set_default_network.return_value = False
                    assert False == set_network_information("mode", "default")

                    mock_set_user_network.return_value = True
                    assert True == set_network_information("mode", "user")

                    mock_set_user_network.return_value = False
                    assert False == set_network_information("mode", "user")

                    mock_read_network_information.return_value = use_network_information["network_PowerOn_mode"]
                    mock_set_user_network.return_value = True
                    assert True == set_network_information("mode", "user")

                    mock_set_user_network.return_value = False
                    assert False == set_network_information("mode", "user")

                    mock_read_network_information.return_value = use_network_information["network_default_mode"]
                    with mock.patch('ee.common.net.__set_ip',return_value = True) as mock_read_network_set_ip:
                        with mock.patch('ee.common.net.__set_mac',return_value = True) as mock_read_network_set_mac:
                            with mock.patch('ee.common.net.__set_mask',return_value = True) as mock_read_network_set_mask:
                                with mock.patch('ee.common.net.__set_gateway',return_value = True) as mock_read_network_set_gateway:
                                    assert True == set_network_information("default:ip", "169.254.1.32")
                                    mock_read_network_set_ip.assert_any_call("169.254.1.32")

                                    assert True == set_network_information("default:mac", "02:0a:35:00:01:32")
                                    mock_read_network_set_mac.assert_any_call("02:0a:35:00:01:32")

                                    assert True == set_network_information("default:mask", "255.255.255.0")
                                    mock_read_network_set_mask.assert_any_call("255.255.255.0")

                                    assert True == set_network_information("default:gateway", "169.254.1.1")
                                    mock_read_network_set_gateway.assert_any_call("169.254.1.1")


def test_read_network_information(use_network_information):
    default_network="#!/bin/bash\n\
mode=\n\
[ $# -ge 1 ] && mode=PowerOn\n\
if [ \"$mode\" == \"PowerOn\" ];then\n\
    ifconfig eth0 down\n\
    ifconfig eth0 hw ether 02:0a:35:00:01:3\n\
    ifconfig eth0 up\n\
    ifconfig eth0 169.254.1.30\n\
    ifconfig eth0 netmask 255.255.255.0\n\
    route add default gw 169.254.1.1\n\
elif [ \"$mode\" == \"user\" ];then\n\
    ifconfig eth0 down\n\
    ifconfig eth0 hw ether 02:0a:35:00:01:4\n\
    ifconfig eth0 up\n\
    ifconfig eth0 169.254.1.31\n\
    ifconfig eth0 netmask 255.255.255.0\n\
    route add default gw 169.254.1.1\n\
elif [ \"$mode\" == \"default\" ];then\n\
    ifconfig eth0 down\n\
    ifconfig eth0 hw ether 02:0a:35:00:01:4\n\
    ifconfig eth0 up\n\
    ifconfig eth0 169.254.1.32\n\
    ifconfig eth0 netmask 255.255.255.0\n\
    route add default gw 169.254.1.1\n\
fi\n"
    fp = open("/opt/seeing/config/network.sh", "w+")
    fp.write(default_network)
    fp.close()
    with mock.patch('ee.common.utility.get_config_path',return_value = "/opt/seeing/config") as mock_get_config_path:
        net_information_dict = read_network_information()
        assert use_network_information["network_default_mode"]["mode"] == net_information_dict["mode"]

        assert use_network_information["network_default_mode"]["default"]["ip"] == net_information_dict["default"]["ip"]
        assert use_network_information["network_default_mode"]["default"]["mac"] == net_information_dict["default"]["mac"]
        assert use_network_information["network_default_mode"]["default"]["mask"] == net_information_dict["default"]["mask"]
        assert use_network_information["network_default_mode"]["default"]["gateway"] == net_information_dict["default"]["gateway"]

        assert use_network_information["network_default_mode"]["user"]["ip"] == net_information_dict["user"]["ip"]
        assert use_network_information["network_default_mode"]["user"]["mac"] == net_information_dict["user"]["mac"]
        assert use_network_information["network_default_mode"]["user"]["mask"] == net_information_dict["user"]["mask"]
        assert use_network_information["network_default_mode"]["user"]["gateway"] == net_information_dict["user"]["gateway"]

        assert use_network_information["network_default_mode"]["PowerOn"]["ip"] == net_information_dict["PowerOn"]["ip"]
        assert use_network_information["network_default_mode"]["PowerOn"]["mac"] == net_information_dict["PowerOn"]["mac"]
        assert use_network_information["network_default_mode"]["PowerOn"]["mask"] == net_information_dict["PowerOn"]["mask"]
        assert use_network_information["network_default_mode"]["PowerOn"]["gateway"] == net_information_dict["PowerOn"]["gateway"]

