# -*- coding:utf-8 -*-
import select
import time
import socket
from threading import Thread
from ee.common import logger

class Tcp2devServer(Thread):
    def __init__(self, device_object, port):
        super(Tcp2devServer, self).__init__()
        self._port = port
        self._connect_socket = None
        self._device = device_object
        self._inputs = []
        self._total_net_size = 0
        self._total_device_size = 0
        self._is_stop = False

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

    def _tcp_to_device(self):
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
        logger.info("recev tcp port %s byte size %d, total recev :%d"%(self._port ,len(data),\
                    self._total_net_size))
        logger.info("tcp to device data:%s"%(logger.print_list2hex(list(bytearray.fromhex(data.encode("hex"))))))

        try:
            self._device.write((data))
        except Exception as e:
            logger.warning("device write data byte size %d error :%s"%(len(data),repr(e)))
            return 0
        return 1

    def _device_to_tcp(self):
        device_data = self._device.read()
        if self._connect_socket is None:
            return 0

        if not device_data:
            return 0
        else :
            self._total_device_size += len(device_data)
            logger.info("device  read data byte size :%d, total read size : %d"%\
                        (len(device_data),self._total_device_size))
            logger.info("device to tcp data:%s"%(logger.print_list2hex(list(bytearray.fromhex(device_data.encode("hex"))))))
            try:
                self._connect_socket.send(bytes(device_data))
                logger.info("client %d send  byte size : %d"%(self._connect_socket.fileno(),len(device_data)))
            except socket.error as e:
                logger.warning("device send to tcp port %s error"%(self._port))
                self._del_connect_socket()

        return 1

    def run(self):
        logger.init("tcp2device.log")
        logger.setLevel("warning")
        try:
            self._server_socket = self._create_server_socket(self._port)
        except socket.error as e:
            logger.boot("create tcp port %d to device server socket failed:%s" %(self._port, repr(e)))
            return
        else:
            logger.boot("create tcp to device server,server socket fd=%s, port=%d" %(self._server_socket.fileno(), self._port))

        self._inputs.append(self._server_socket)
        while not self._is_stop:
            '''nonboclking mode to poll the socket'''
            read_able_list = select.select(self._inputs, [], [], 0)[0]

            if self._server_socket in read_able_list:
                client,addr=self._server_socket.accept()
                self._del_connect_socket()
                self._add_connect_socket(client)
                continue

            if self._connect_socket in read_able_list:
                try:
                    self._tcp_to_device()
                except Exception as e:
                    logger.error("tcp port %s to deivce error:%s"%(self._port, repr(e)))
                    break

            try:
                ret_device2tcp = self._device_to_tcp()
            except Exception as e:
                logger.error("device to tcp port %s error:%s"%(self._port, repr(e)))
                break

            if ret_device2tcp == 0 and len(read_able_list) == 0:
                time.sleep(0.1)

        self._del_connect_socket()
        self._server_socket.close()

    def stop(self):
        self._is_stop = True