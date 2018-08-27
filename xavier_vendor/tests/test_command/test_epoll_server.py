# -*- coding:utf-8 -*-
import pytest
import os
import sys
import signal
import socket
import time
'''
sys.path.append("../..")
from command.server import epoll_server

port = 1106
host = "127.0.0.1"
addr = (host, port)

@pytest.fixture(scope='function')
def setup_function(request):
    def teardown_function():
        print("teardown_function called.")
    request.addfinalizer(teardown_function)
    print('setup_function called.')

@pytest.fixture(scope='module')
def setup_module(request):
    def teardown_module():
        os.kill(pid, signal.SIGKILL)
    request.addfinalizer(teardown_module)
    try:
        pid = os.fork()
    except OSError, error:
        os._exit(1)
    if (pid == 0):
        epoll_server.create_srv("tcp:1106")
        epoll_server.run_server()

def test_1(setup_module):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(3)
    sock.send("[1123]version(?)\r\n")
    string = sock.recv(1024)
    assert "[1123]ACK(version(<number>)$" == string[0:28]
    sock.close()

def test_2(setup_module):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(3)
    sock.send("   [1123]   version   (     ? ,,,, ,,,  )\r\n")
    string = sock.recv(1024)
    assert "[1123]ACK(version(<number>)$" == string[0:28]
    sock.close()

def test_3():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(3)
    for i in range(0, 100):
        sock.send("    [1123]  version   (?)    \r\n")
        assert "[1123]ACK(version(<number>)$" == sock.recv(1024)[0:28]
    sock.close()

def test_4():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.send("[1123]version(?)\n")
    sock.settimeout(3)
    try:
        string = sock.recv(1024)
        assert "" == string
    except socket.timeout as timeout:
        assert str(timeout) == 'timed out'
    sock.close()

def test_5():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(3)
    sock.send("\r\n\r\n\r\n[1123]version(?)\r\n\r\n\r\n")
    sock.settimeout(3)
    string = sock.recv(1024)
    assert "[1123]ACK(version(<number>)$" == string[0:28]
    sock.close()

def test_6():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(3)
    sock.send("\r\n\r\n\r\n")
    sock.settimeout(3)
    try:
        string = sock.recv(1024)
        assert "" == string
    except socket.timeout as timeout:
        assert str(timeout) == 'timed out'
    sock.close()

def test_7():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(3)
    sock.send("[1123]版本(?)\r\n")
    string = sock.recv(1024)
    assert "[1123]ACK(ERR_-14:" == string[:18]
    sock.close()

def test_8():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(3)
    sock.send("[1123]display version(?)\r\n")
    string = sock.recv(1024)
    assert "[1123]ACK(ERR_-190:" == string[:19]
    sock.close()

def test_9():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(3)
    sock.send("[1123]displaydisplaydisplaydisplaydisplaydisplaydisplaydisplaydisplaydisplaydisplaydisplaydisplaydispalydispaaaasssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssfffffffffffffffffffffffffdddddddddddddddddd(?)\r\n")
    string = sock.recv(1024)
    assert "[1123]ACK(ERR_-4:" == string[:17]
    sock.close()
'''