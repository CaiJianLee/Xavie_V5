import pytest
import os
import sys
'''
sys.path.append("../..")
from command.server.decode import *

def test_1():
    arg = "[1122]gpio set(?)"
    decode_command = libcmd.sg_cmd_decode(arg)
    assert "1122" == decode_command.sCommandID
    assert "gpio set" == decode_command.sCommandKeyword
    assert "?" == decode_command.sCommandParameters

def test_2():
    arg = "[1122         ]         gpio set      (            ?       )"
    decode_command = libcmd.sg_cmd_decode(arg)
    assert "1122         " == decode_command.sCommandID
    assert "gpio set" == decode_command.sCommandKeyword
    assert "?" == decode_command.sCommandParameters

def test_3():
    arg = "[    1122     ]         gpio set      (            ?    ,   )                    "
    decode_command = libcmd.sg_cmd_decode(arg)
    assert "    1122     " == decode_command.sCommandID
    assert "gpio set" == decode_command.sCommandKeyword
    assert "?" == decode_command.sCommandParameters

def test_4():
    arg = "[    1122     ]  gpio    set      (            ?  , ,,,,,1       )                    "
    decode_command = libcmd.sg_cmd_decode(arg)
    assert "    1122     " == decode_command.sCommandID
    assert "gpio set" == decode_command.sCommandKeyword
    assert "?,1" == decode_command.sCommandParameters

def test_5():
    arg = "[  11  22     ]  gpio   set      (            ?  , ,,,,,1       )                    "
    decode_command = libcmd.sg_cmd_decode(arg)
    assert "  11  22     " == decode_command.sCommandID
    assert "gpio set" == decode_command.sCommandKeyword
    assert "?,1" == decode_command.sCommandParameters

def test_6():
    arg = "      [  11  22     ]  gpio   set      (            ?  , ,,,,,1       )                    "
    decode_command = libcmd.sg_cmd_decode(arg)
    assert "  11  22     " == decode_command.sCommandID
    assert "gpio set" == decode_command.sCommandKeyword
    assert "?,1" == decode_command.sCommandParameters

def test_7():
    arg = "    [1123]  gpio    set (?)   "
    decode_command = libcmd.sg_cmd_decode(arg)
    assert "1123" == decode_command.sCommandID
    assert "gpio set" == decode_command.sCommandKeyword
    assert "?" == decode_command.sCommandParameters

def test_8():
    arg = "  [1234567890122345] gpio set (?)"
    decode_command = libcmd.sg_cmd_decode(arg)
    assert -3 == decode_command.nErrorNO
    assert "None" == decode_command.sCommandID

'''