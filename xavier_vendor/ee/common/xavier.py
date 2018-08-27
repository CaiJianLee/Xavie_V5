# -*- coding:utf-8 -*-
import time
import zmq
import json
import socket
import traceback
from ee.common import logger
from ee.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from ee.tinyrpc.transports.zmq import ZmqClientTransport
from ee.tinyrpc.proxy.eeproxy import EEProxy
from ee.tinyrpc.exc import RPCError

def init_proxy(server='tcp://127.0.0.1:22700'):
    ctx = zmq.Context()
    global proxy
    proxy = EEProxy(
            JSONRPCProtocol(),
            ZmqClientTransport.create(ctx, server)
    )

def call(handle, *args, **kwargs):
    try:
        type(proxy)
    except Exception:
        init_proxy()
    return proxy.call(handle, args, kwargs)


class XavierRpcClient():
    def __init__(self, ip, port, mode="zmq"):
        self._ip = ip
        self._port = int(port)
        self._mode = mode
        self._protocol = JSONRPCProtocol()
        self.sock = self._create_conn()

    def call(self, handle, *args, **kwargs):
        req = self._protocol.create_request(handle, args, kwargs, False)
        protocol = req.serialize()
        if self._mode == "tcp":
            protocol = protocol + "\n"
        self.sock.send(protocol)
        reply = self.sock.recv(40960)
        if self._mode == "tcp":
            self.sock.close()
            self.sock = self.__create_tcp_conn()

        return self._result_protocol(reply)

    def __create_req_conn(self):
        HOST = self._ip
        PORT = self._port
        context = zmq.Context()
        sock = context.socket(zmq.REQ)
        sock.connect("tcp://%s:%d"%(HOST, PORT))
        return sock

    def __create_tcp_conn(self):
        HOST = self._ip
        PORT = self._port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.connect((HOST, PORT))
        except Exception as e:
            logger.error("connect %s exception : %s"%(str((HOST, PORT)), traceback.format_exc()))
        return sock

    def _create_conn(self):
        if self._mode == "tcp":
            return self.__create_tcp_conn()
        elif self._mode == "zmq":
            return self.__create_req_conn()
        else:
            logger.warning("no support mode:%s"%(msg_json["mode"]))
        return None

    def _result_protocol(self, reply):
        response = self._protocol.parse_reply(reply)
        if hasattr(response, 'error'):
            raise RPCError('Error calling remote procedure: %s' %\
                           response.error)

        return response.result
