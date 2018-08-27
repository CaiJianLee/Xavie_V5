# -*- coding: utf-8 -*-

import socket
import json
import collections
import encodings.idna
from ee.common import logger

class DDPClient:
    
    def __init__(self, host, port):
        self.ddpsocket = None
        self._host = host
        self._port = port
        self._unique_id = 0
        
    def __del__(self):
        if self.ddpsocket is not None:
            #self.ddpsocket.shutdown(SHUT_RDWR)
            self.ddpsocket.close()
        
    def _next_id(self):
        self._unique_id += 1
        return str(self._unique_id)
    
    def start(self):
        try: 
            self.ddpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except OSError as e:
            logger.error("Error creating socket:" +str(e))
            self.ddpsocket = None
            return False
            
        try:
            addr = (self._host, self._port)
            self.ddpsocket.connect(addr)
        except socket.gaierror as e:
            logger.error("Address-related error connection to server: " +str( e))
            self.ddpsocket.close()
            self.ddpsocket = None
            return False
        except socket.error as e:
            logger.error("Connection error:"+str(e))
            self.ddpsocket.close()
            return False
            
        return True
    
    def stop(self):
        if self.ddpsocket is not None:
            #self.ddpsocket.shutdown(SHUT_RDWR)
            self.ddpsocket.close()
        
    def send(self, msg):
        msg = json.dumps(msg, separators=(',',':'))
        msg += '\r\n'
        logger.debug('ddp send msg:'+str(msg))
        return self.ddpsocket.send(msg.encode())
    
    def recv(self, bufsize):
        result =self.ddpsocket.recv(bufsize)
        logger.debug('ddp recv:'+ str(result))
        return json.loads(result.decode())
     
    def call(self, method, params):
        current_id = self._next_id()
        msg = collections.OrderedDict()
        msg['msg'] = method
        msg['id'] = current_id
        msg['params'] = params
        try:
            self.send(msg)
            result = self.recv(2048)
        except Exception as e:
            logger.error('ddp send msg:'+str(e))
            return False
        return result
    
    
    