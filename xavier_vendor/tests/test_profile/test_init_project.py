# -*- coding:utf-8 -*-
__author__ = 'Haite and zhenhua'

import os
import json
import mock
import pytest

from ee.profile.profile import Profile
from ee.profile.parser import ProfileParser
import ee.initializer as Initer
from ee.chip import *
from ee.board import *
#from ee.common import logger

@pytest.fixture
def jsonfile():
    return os.getcwd() + '/tests/test_profile/test.json'

def test_init_project(jsonfile):
    #logger.init("test_init_project.log")
    #logger.setLevel("debug")
    from ee.profile.xobj import XObject
    with mock.patch.object(CAT9555, "__init__", return_value=None) as mock_init_cat9555:
        with mock.patch.object(Dmm001001,"__init__", return_value=None) as mock_init_dmm001:
            with mock.patch.object(AD5667,"__init__", return_value=None) as mock_init_ad5667:
                with mock.patch.object(CAT9555,"write_dir_config", return_value=True) as mock_write_dir_config:
                    with mock.patch.object(CAT9555,"write_outport", return_value=True) as mock_write_outport:
                        with mock.patch.object(Dmm001001,"board_initial", return_value=True) as mock_dmm_board_initial:
                            with mock.patch.object(Vfreq001001,"__init__", return_value=None) as mock_init_vfreq001:
                                with mock.patch.object(Vfreq001001,"board_initial", return_value=True) as mock_vfreq_board_initial:
                                    with mock.patch.object(TCA9548, "__init__", return_value=None) as mock_init_tca:
                                        with mock.patch.object(Scope002001A,"__init__", return_value=None) as mock_init_scope002:
                                            with mock.patch.object(Scope002001A,"board_initial", return_value=True) as mock_scope_board_initial:
                                                with mock.patch.object(Vvo001001,"__init__", return_value=None) as mock_init_vvo001:
                                                    with mock.patch.object(Vvo001001,"board_initial", return_value=True) as mock_vvo_board_initial:
                                                        parser = ProfileParser()
                                                        classes = globals()
                                                        XObject._classes = classes
                                                        parser.read_profile(jsonfile)
                                                        Initer._create_chip_object()
                                                        Initer._create_board_object()
                                                        Initer._init_board()
                                                        assert mock_init_cat9555.call_count == 8
                                                        mock_init_dmm001.assert_called_once_with(Profile.get_board_by_name('dmm'))
                                                        mock_init_vfreq001.assert_called_once_with(Profile.get_board_by_name('freq'))
                                                        mock_init_scope002.assert_called_once_with(Profile.get_board_by_name('datalogger'))
                                                        mock_init_vvo001.assert_called_once_with(Profile.get_board_by_name('voltage_output'))
 
def test_initconfig():
    initconfig = Profile.get_initconfig()
    assert len(initconfig['extendio']['instrument']) == 8
    assert len(initconfig['boards']) == 4
 
    assert initconfig['extendio']['instrument']['cp1']['value'][0] == int('0x0',16)
    assert initconfig['extendio']['instrument']['cp1']['value'][1] == int('0x0',16)
    assert initconfig['extendio']['instrument']['cp1']['dir'][0] == int('0x1f',16)
    assert initconfig['extendio']['instrument']['cp1']['dir'][1] == int('0x0',16)
 
def test_get_class():
    from ee.profile.xobj import XObject
    #assert len(XObject._objects.keys()) == 24
 
    assert str(type(XObject.get_object("cp1"))) == "<class 'ee.chip.cat9555.CAT9555'>"
    assert str(type(XObject.get_object("cp2"))) == "<class 'ee.chip.cat9555.CAT9555'>"
    assert str(type(XObject.get_object("cp3"))) == "<class 'ee.chip.cat9555.CAT9555'>"
    assert str(type(XObject.get_object("cp4"))) == "<class 'ee.chip.cat9555.CAT9555'>"
    assert str(type(XObject.get_object("cp5"))) == "<class 'ee.chip.cat9555.CAT9555'>"
    assert str(type(XObject.get_object("cp6"))) == "<class 'ee.chip.cat9555.CAT9555'>"
    assert str(type(XObject.get_object("cp7"))) == "<class 'ee.chip.cat9555.CAT9555'>"
    assert str(type(XObject.get_object("cp8"))) == "<class 'ee.chip.cat9555.CAT9555'>"

    assert str(type(XObject.get_object("dmm"))) == "<class 'ee.board.dmm001.dmm001001.Dmm001001'>"
    assert str(type(XObject.get_object("datalogger"))) == "<class 'ee.board.scope002.scope002001A.Scope002001A'>"
    assert str(type(XObject.get_object("freq"))) == "<class 'ee.board.vfreq001.vfreq001001.Vfreq001001'>"
    assert str(type(XObject.get_object("voltage_output"))) == "<class 'ee.board.ins001.vvo001001.Vvo001001'>"

def test_init_net(jsonfile):
    with mock.patch('ee.common.utility.get_config_path') as mock_get_config_path:
       with mock.patch('os.path.exists') as mock_path_exists:
          with mock.patch('ee.common.net.set_default_network') as mock_set_default_network:
            with mock.patch('ee.initializer._write_default_net') as mock_write_default_net:
                with mock.patch('ee.common.net.set_network') as mock_set_network:
                    with mock.patch('ee.common.net.read_network_information') as mock_read_network_information:
                        mock_read_network_information.return_value = {"mode":"default","default":{"ip":"192.168.99.10"}}
                        mock_get_config_path.return_value = "/opt/seeing/config"
                        
                        mock_path_exists.return_value = True
                        mock_write_default_net.return_value = True
                        mock_set_network.return_value = True
                        assert True == Initer._init_net()

                        mock_path_exists.return_value = False
                        mock_write_default_net.return_value = False
                        assert False == Initer._init_net()

                        mock_path_exists.return_value = False
                        mock_write_default_net.return_value = True
                        mock_set_network.return_value = False
                        assert True == Initer._init_net()

def test_write_default_net(jsonfile):
    with mock.patch.object(Profile,'get_initconfig') as mock_get_initconfig:
        with mock.patch('ee.common.net.network_config') as mock_network_config:
            with mock.patch('ee.overlay.extendio.get') as mock_get:
                with mock.patch.object(Profile,'get_extendio_by_name', return_value = []) as mock_get_extendio_by_name:
                    with mock.patch('ee.common.net.read_network_information') as mock_read_network_information:
                        with mock.patch('ee.common.utility.get_config_path',return_value = "/opt/seeing/config") as mock_get_config_path:
                            with mock.patch('ee.common.net.set_network_information') as mock_set_network_information:
                                mock_get_initconfig.return_value = {"netconfig":{"netio":[{"id": "netio_1", "bit": "bit1"},]}}
                                mock_network_config.return_value = mock.Mock()
                                mock_get.return_value = {"bit1":1}
                                mock_read_network_information.return_value = {"mode":"default","default":{"ip":"192.168.99.10"}}
                                mock_set_network_information.return_value = True
                                assert True == Initer._write_default_net()

                                mock_get_initconfig.return_value = {"netconfig":{}}
                                assert True == Initer._write_default_net()

                                with mock.patch('ee.initializer._get_network_num') as mock_get_network_num:
                                    with mock.patch('ee.common.net.write_network_information') as mock_write_network_information:
                                        mock_get_network_num.return_value = -1
                                        mock_read_network_information.return_value = {"mode":"user","PowerOn":{"ip":"192.168.99.3",\
                                                                                                                                                                        "mac":"02:0a:35:00:01:03",\
                                                                                                                                                                        "mask":"255.255.255.0",\
                                                                                                                                                                        "gateway":"192.168.99.1"}}
                                        assert True == Initer._write_default_net()
                                        mock_write_network_information.assert_any_call("default:ip","192.168.99.3")
                                        mock_write_network_information.assert_any_call("default:mac","02:0a:35:00:01:03")
                                        mock_write_network_information.assert_any_call("default:mask","255.255.255.0")
                                        mock_write_network_information.assert_any_call("default:gateway","192.168.99.1")
                                        mock_read_network_information.return_value = {"mode":"default","default":{"ip":"192.168.99.10"}}
                                        assert False == Initer._write_default_net()


