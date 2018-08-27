# -*- coding:utf-8 -*-
import select
import time
import socket
from threading import Thread
from ee.common import logger
from ee.profile.xobj import XObject
from ee.profile.profile import Profile

class UartServer(Thread):
    def __init__(self, uartname, port):
        super(UartServer, self).__init__()
        self._uartname = uartname
        self._port = port
        self._connect_socket = None
        self._uart_device = XObject.get_object(uartname)
        self._inputs = []
        self._total_net_size = 0
        self._total_uart_size = 0
        self._uart_stop = False

    def _create_server_socket(self, port):
        try:
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            raise e

        try:
            serversocket.setblocking(False)
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            addr = ("0.0.0.0", port)
            serversocket.bind(addr)
            serversocket.listen(5)
        except socket.error as e:
            serversocket.close()
            raise e

        return serversocket

    def _add_connect_socket(self, client):
        if self._connect_socket is not None:
            self._del_connect_socket()
        self._inputs.append(client)
        self._connect_socket = client
        logger.info("add connected socket fd = %d"%(client.fileno()))

    def _del_connect_socket(self):
        if self._connect_socket is not None:
            self._inputs.remove(self._connect_socket)
            self._connect_socket.close()
            self._connect_socket = None

    def _net_to_uart(self):
        try:
            data = self._connect_socket.recv(2048)
        except socket.error as e:
            logger.warning("read %d socket error:%s"%(self._connect_socket.fileno(), repr(e)))
            self._del_connect_socket()
            return 0
        
        if len(data) == 0:
            self._del_connect_socket()
            return 0

        self._total_net_size += len(data)
        logger.info("recev %s net byte size %d total recev :%d"%(self._uartname ,len(data),\
                    self._total_net_size))
        logger.info("net to uart data:%s"%(logger.print_list2hex(list(bytearray.fromhex(data.encode("hex"))))))

        try:
            self._uart_device.write((data))
        except Exception as e:
            logger.warning("write %s device error %s"%(self._uartname,repr(e)))
            return 0
        return 1

    def _uart_to_net(self):
        uart_data = self._uart_device.read()
        if self._connect_socket is None:
            return 0

        if not uart_data:
            return 0
        else :
            self._total_uart_size += len(uart_data)
            logger.info(" read %s data byte size :%d total read size : %d"%\
                        (self._uartname,len(uart_data),self._total_uart_size))
            logger.info("uart to net data:%s"%(logger.print_list2hex(list(bytearray.fromhex(uart_data.encode("hex"))))))
            try:
                self._connect_socket.send(bytes(uart_data))
                logger.info("client %d send  byte size : %d"%(self._connect_socket.fileno(),len(uart_data)))
            except socket.error as e:
                logger.warning("device %s net send error"%(self._uartname))
                self._del_connect_socket()

        return 1

    def run(self):
        logger.init("uart2net.log")
        logger.setLevel("warning")
        try:
            self._server_socket = self._create_server_socket(self._port)
        except socket.error as e:
            logger.boot("%s device create port %d server socket failed:%s" %(self._uartname, self._port, repr(e)))
            return
        else:
            logger.boot("%s device create server socket fd=%s port=%d" %(self._uartname, self._server_socket.fileno(), self._port))

        self._inputs.append(self._server_socket)

        while not self._uart_stop:
            '''nonboclking mode to poll the socket'''
            read_able_list = select.select(self._inputs, [], [], 0)[0]

            if self._server_socket in read_able_list:
                client,addr=self._server_socket.accept()
                self._del_connect_socket()
                self._add_connect_socket(client)
                continue

            if self._connect_socket in read_able_list:
                try:
                    self._net_to_uart()
                except Exception as e:
                    logger.error("%s net to uart error:%s"%(self._uartname, repr(e)))
                    break

            try:
                ret_uart2net = self._uart_to_net()
            except Exception as e:
                logger.error("%s uart to net error:%s"%(self._uartname, repr(e)))
                break

            if ret_uart2net == 0 and len(read_able_list) == 0:
                time.sleep(0.05)

        self._del_connect_socket()
        self._server_socket.close()

    def stop(self):
        self._uart_stop = True

def create_uart_server():
    for name, bus in Profile.get_buses().iteritems():
        if bus['bus'] == 'uart' and bus.has_key('port'):
            uartserver = UartServer(name, bus['port'])
            uartserver.start()