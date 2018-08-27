import os
import socket
import select
import ctypes
from command.server import decode
from ee.bus import uart
from timeit import Timer
from time import clock
from command.server import handler
from ee.common import logger
dev_list = []

READ_ONLY = (select.EPOLLIN | select.EPOLLHUP | select.EPOLLPRI | select.EPOLLERR)
READ_WRITE = (READ_ONLY | select.EPOLLOUT)

global request_uart
request_uart = {}

'''
@func : __create_tcp_srv
'''
def __create_tcp_srv(port):
    HOST = "0.0.0.0"
    PORT = int(port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    dev_sock = {}
    dev_sock["type"] = "tcp"
    dev_sock["fd"]   = sock
    dev_cnt = len(dev_list)
    dev_list.append(dev_sock)
    return dev_cnt

'''
@func : __create_uart_srv
'''
def __create_uart_srv(port, baudrate):
    _uart = uart.UartBus(port)
    _uart.config(baudrate)
    dev_uart = {}
    dev_uart["type"] = "uart"
    dev_cnt = len(dev_list)
    dev_uart["fd"]   = _uart
    dev_list.append(dev_uart)
    return dev_cnt
    


'''
@name : create_srv
@func : user create server;
@e.g. : create_srv("tcp:1106")   create tcp server with port 1106
@       create_srv("uart:/dev/ttyPS0,115200")   create uart server, device is /dev/ttyPS0, baudrate 115200
'''
def create_srv(*args):
    temp_list = args[0].split(":")
    if "tcp" == temp_list[0].strip():
        return __create_tcp_srv(temp_list[1].strip())
    elif "uart" == temp_list[0].strip():
        _uart = temp_list[1].strip().split(",")
        if (len(_uart) == 1):
            return __create_uart_srv(_uart[0].strip(), 115200)
        elif (len(_uart) == 2):
            return __create_uart_srv(_uart[0].strip(), int(_uart[1].strip()))
    else:
        return False

'''
@func : __poll_srv
'''
def __poll_srv(poll):
    for dev in dev_list:
        if "tcp" == dev["type"]:
            dev["fd"].listen(100)
            poll.register(dev["fd"].fileno(), READ_ONLY)
        elif "uart" == dev["type"]:
            global request_uart
            poll.register(dev["fd"].fileno(), READ_ONLY)
            request_uart[dev["fd"].fileno()] = decode.SeNetWorkCustomRecv()
            decode.sg_network_init(ctypes.byref(request_uart[dev["fd"].fileno()]))
        else:
            continue
    return None

'''
@func : __unpoll_srv
'''
def __unpoll_srv(poll):
    for dev in dev_list:
        if "tcp" == dev["type"]:
            poll.unregister(dev["fd"].fileno())
            dev["fd"].close()
        elif "uart" == dev["type"]:
            poll.unregister(dev["fd"].fileno())
            dev["fd"].close()
    poll.close()
    return None

'''
@func : __get_dev
'''
def __get_dev(fileno):
    ret = 0
    for dev in dev_list:
        if fileno == dev["fd"].fileno():
            return dev
    return None

'''
@name : run_server
@func : user run server after create servers
@e.g. : run_server()
'''
def run_server():
    epoll = select.epoll()
    __poll_srv(epoll)
    connections = {}
    requests    = {}
    info = {}
    while True:
        try:
            events = epoll.poll()
        except Exception:
            continue
        for fileno, event in events:
            if (event & (select.POLLIN | select.POLLPRI)) :
                dev = __get_dev(fileno)
                if (None != dev):
                    if ("uart" == dev["type"]):
                        global request_uart
                        recv_buff = dev["fd"].read(decode.CONFIG_TERMINAL_RECV_LENGTH - request_uart[dev["fd"].fileno()].iRecvBufferTailCursor)
                        request_uart[dev["fd"].fileno()].sRecvBuffer = request_uart[dev["fd"].fileno()].sRecvBuffer + recv_buff
                        request_uart[dev["fd"].fileno()].iRecvBufferTailCursor = len(request_uart[dev["fd"].fileno()].sRecvBuffer)
                        while (0 == decode.sg_get_cmd(ctypes.byref(request_uart[dev["fd"].fileno()]))):
                            str_recv = request_uart[dev["fd"].fileno()].sRecvBuffer
                            decode_command = decode.sg_decode(str_recv)
                            result = str(handler.call_handle(decode_command.sCommandKeyword, decode_command.sCommandParameters))
                            ret = decode.sg_call_result(ctypes.byref(decode_command), result, len(result))
                            if (0 == ret):
                                dev["fd"].write(decode_command.sCommandReply)
                            decode.sg_destroy_result(ctypes.byref(decode_command))
                        break
                    elif ("tcp" == dev["type"]):
                        connection, addr = dev["fd"].accept()
                        info[connection.fileno()] = addr
                        connection.setblocking(0)
                        epoll.register(connection, READ_ONLY)
                        connections[connection.fileno()] = connection
                        requests[connection.fileno()] = decode.SeNetWorkCustomRecv()
                        decode.sg_network_init(ctypes.byref(requests[connection.fileno()]))
                        logger.warning("ip[%s], port[%s] connected"%(addr))
                else:
                    if (0 == decode.sg_recv(ctypes.c_int(fileno), ctypes.byref(requests[fileno]))):
                        epoll.modify(fileno, READ_WRITE)
                    else:
                        logger.warning("socket:%d break"%(fileno))
                        epoll.unregister(fileno)
                        del requests[fileno]
                        connections[fileno].close()
                        logger.warning("ip[%s], port[%s] connection remote"%(info[fileno]))
                        del info[fileno]
            elif (event & select.EPOLLOUT):
                try:
                    while (0 == decode.sg_get_cmd(ctypes.byref(requests[fileno]))):
                        str_recv = requests[fileno].sRecvBuffer
                        decode_command = decode.sg_decode(str_recv)
                        result = str(handler.call_handle(decode_command.sCommandKeyword, decode_command.sCommandParameters))
                        ret = decode.sg_call_result(ctypes.byref(decode_command), result, len(result))
                        if (0 == ret):
                            decode.sg_send(fileno, decode_command.sCommandReply, len(decode_command.sCommandReply))
                        decode.sg_destroy_result(ctypes.byref(decode_command))
                except Exception:
                    pass
                epoll.modify(fileno, READ_ONLY)
            elif (event & select.EPOLLHUP):
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
                del requests[fileno]
                logger.warning("ip[%s], port[%s] connection remote"%(info[fileno]))
                del info[fileno]
    return True
