import pytest
import mock
import socket
import os
import sys
import signal
import time
from ee.uart_server import UartServer
from ee.bus.uart import UartBus
from ee.ipcore.axi4_uart import Axi4Uart
from ee.profile.xobj import XObject

uart_list={
    'ps_uart':{'path': '/dev/ps_uart', 'baudrate': '115200', 'type': 'uart', 'port': 7641},
    'pl_uart':{'path': '/dev/pl_uart', 'baudrate': '115200', 'type': 'uart', 'ip_core': 'Axi4Uart', 'port': 7643}
}

port = 7641
host = "127.0.0.1"
addr = (host, port)

@pytest.fixture(scope="module")
def ps_uart_server():
    with mock.patch.object(XObject,'get_object',return_value=mock.Mock()) as mock_profile_getclass:
        return UartServer('ps_uart', uart_list['ps_uart']['port'])

def test_ps_init(ps_uart_server):
    assert ps_uart_server._uartname == 'ps_uart'
    assert ps_uart_server._port == 7641
    assert ps_uart_server._uart_device != False

@pytest.fixture(scope='module')
def setup_module(request, ps_uart_server):
    def teardown_module():
        os.kill(pid, signal.SIGKILL)
    request.addfinalizer(teardown_module)
    try:
        pid = os.fork()
    except OSError, error:
        os._exit(1)
    if (pid == 0):
        ps_uart_server._uart_device.read = mock.Mock()
        ps_uart_server._uart_device.read.return_value=list([0x65,0x66])
        ps_uart_server._uart_device.write = mock.Mock()
        ps_uart_server.run()

def test_uart_to_net(setup_module):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    time.sleep(0.5)
    ret = sock.connect_ex(addr)
    print ret
    #time.sleep(0.5)
    data = sock.recv(1024)
    assert data[:10] == bytes([0x65,0x66])
    sock.close()