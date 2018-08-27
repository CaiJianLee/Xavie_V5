import zmq
import socket
import ctypes
import threading
import traceback
from time import clock
import time
from ee.common import logger
import ee.common.utility as utility

libdaq = ctypes.cdll.LoadLibrary(utility.get_lib_path() + "/libsgdaq.so")

class DataChannel(threading.Thread):
    def __init__(self, name, port, channelid, sub_filters, data_filters):
        super(DataChannel, self).__init__()
        logger.boot("create %s channel port=%d, id=%d, sub_filters=%r, data_filters=%r" %(name, port, channelid, sub_filters, data_filters)) 
        self._name = name
        self._port = port
        self._channelid = channelid
        self._connector = None
        self._sub_filters = sub_filters
        self._data_filters = data_filters
        self._channel_stop = False
        self._controller = None
        self._debug = None

    def __destruction(self):
        for sub_filter in self._sub_filters:
            if sub_filter['type'] == "all" and sub_filter['chipnum'] == "all":
                libdaq.delete_channel(255, 255)
                break
            libdaq.delete_channel(sub_filter['type'], sub_filter['chipnum'])

    def set_sub_filters(self, sub_filters):
        self._sub_filters = sub_filters

    def add_sub_filter(self, sub_filter):
        self._sub_filters.append(sub_filter)
    
    def set_data_filters(self, data_filters):
        self._data_filters = data_filters

    def _run(self):
        logger.init('daq.log')
        try:
            listener = self._create_listen_socket(self._port)
        except socket.error, e:
            logger.boot("%s channel create listen socket failed:%s" %(self._name, e))
            return 
        else:
            logger.boot("%s channel create listen socket fd=%d" %(self._name, listener.fileno()))

        subscriber = self._create_subscriber(self._sub_filters)
        
        poller = zmq.Poller()
        self._poller = poller
        poller.register(listener.fileno(), zmq.POLLIN)
        poller.register(subscriber, zmq.POLLIN)
        conn_addr = None

        while not self._channel_stop:
            socks = dict(poller.poll())

            # accept the new connect
            if listener.fileno() in socks:
                conn, addr = listener.accept()
                conn_addr = addr
                logger.warning("%s channel accept connection from %s, %d, fd = %d" %(self._name, addr[0], addr[1], conn.fileno()))
                if self._connector is not None:
                    logger.error("%s channel remote connector socket replaced by %d with %d" %(self._name, self._connector.fileno(), conn.fileno()))
                    self.remove_connector()

                self._connector = conn
                poller.register(self._connector.fileno(), zmq.POLLIN)
                self._connector.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._connector.settimeout(2)

            # receive packet from data acquisitor publisher
            if subscriber in socks:
                try:
                    addr = subscriber.recv()
                    frame = subscriber.recv()
                except zmq.ZMQError, e:
                    if e.errno == zmq.ETERM:
                        logger.error("%s channel subscriber interrupte" %(self._name))
                        break
                    else:
                        logger.error("%s channel receive data error: %s" %(self._name, e))

                if self._connector is not None:
                    frame_list = [frame]
                    self._process_frame(frame_list)

                if self._controller != None:
                    try:
                        self._controller.send("")
                    except Exception as e:
                        if self._debug is not subscriber:
                            logger.warning("%s request send err : %s"%(addr, str(e)))
                        else:
                            logger.warning("%s request send err : %s"%("frame://all:all", str(e)))
                        continue
                    try:
                        message = self._controller.recv(32)
                    except zmq.error.Again:
                        if self._debug is not subscriber:
                            logger.warning("%s request time out"%(addr))
                        else:
                            logger.warning("%s request time out"%("frame://all:all"))

            # receive packet from remote 
            if self._connector is not None and self._connector.fileno() in socks:
                try:
                    data = self._connector.recv(1024)
                except socket.error, e:
                    logger.error("%s channel's connector[%s, %d], fd[%d] error: %s" \
                                 %(self._name, conn_addr[0], conn_addr[1], self._connector.fileno(), e))
                    self.remove_connector()
                else:
                    if not data:
                        logger.warning("%s channel's connector[%s, %d], fd[%d] had been closed by client" \
                                       %(self._name, conn_addr[0], conn_addr[1], self._connector.fileno()))
                        self.remove_connector()

        subscriber.close()
        self._context.term()
        self._connector.close()
        listener.close()

    def run(self):
        try:
            self._run()
        except Exception:
            logger.error("port = %d , traceback : %s"%(self._port, traceback.format_exc()))
        self.__destruction()

    def stop(self):
        self._channel_stop = True; 

    def _create_listen_socket(self, port):
        try:
            listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error:
            raise
            
        try:
            listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            listen_fd.close()
            raise

        addr = ("0.0.0.0", port)
        try:
            listen_fd.bind(addr)
        except socket.error:
            listen_fd.close()
            raise
            
        try:
            listen_fd.listen(8)
        except socket.error:
            listen_fd.close()
            raise

        return listen_fd

    def _create_subscriber(self, sub_filters):
        self._context = zmq.Context()
        subscriber = self._context.socket(zmq.SUB)
        subscriber.connect("tcp://localhost:22720")
        
        # set the subscribe filter
        for sub_filter in sub_filters:
            if sub_filter['type'] == "all" and sub_filter['chipnum'] == "all":
                logger.boot("%s channel add subscriber filter: frame://%s:%s"%(self._name, sub_filter['type'], sub_filter['chipnum']))
                subscriber.setsockopt(zmq.SUBSCRIBE, "")
                if self._controller is None:
                    self._controller = self._context.socket(zmq.REQ)
                    self._controller.connect("tcp://localhost:22770")
                libdaq.add_channel(255, 255)
                self._debug = subscriber
                break
            logger.boot("%s channel add subscriber filter: frame://%d:%d"%(self._name, sub_filter['type'], sub_filter['chipnum']))
            subscriber.setsockopt(zmq.SUBSCRIBE, "frame://%d:%d"%(sub_filter['type'], sub_filter['chipnum']))
            if self._controller is None:
                self._controller = self._context.socket(zmq.REQ)
                self._controller.connect("tcp://localhost:22770")
            libdaq.add_channel(sub_filter['type'], sub_filter['chipnum'])
        return subscriber
    
    def _process_frame(self, frame_list):
        for data_filter in self._data_filters:
            state, desp = data_filter(self, frame_list)
            if state == "Done" :
                break
                        
            if state == "Error":
                logger.error("%s channel's %r filter handle data failed:%s" %(self._name, data_filter, desp))
                break

    def remove_connector(self):
        self._poller.unregister(self._connector.fileno())
        try:
            self._connector.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        self._connector.close()
        self._connector = None


class DataChannelEx():
    def __init__(self, id, port, ch, sub_filters, data_filters):
        self._id = id;
        self._port = port;
        self._ch = ch;
        self._sub_filters = sub_filters;
        self._data_filters = data_filters;

    def __encode(self):
        msg = ""
        frame_type = ""
        chipnum = ""
        data_filters = ""
        for sub_filter in self._sub_filters:
            if frame_type == "":
                if sub_filter["type"] == "all":
                    frame_type = "255"
                else:
                    frame_type = str(sub_filter["type"])
            if chipnum == "":
                if sub_filter["chipnum"] == "all":
                    chipnum = "255"
                else:
                    chipnum = str(sub_filter["chipnum"])
            else:
                chipnum = chipnum + "," + str(sub_filter["chipnum"])
        for data_filter in self._data_filters:
            if data_filters == "":
                data_filters = str(data_filter)
            else:
                data_filters = data_filters + "," + str(data_filter)
        
        msg = "0:" + str(self._id) + ";1:" + str(self._port) + ";2:" + str(frame_type) + \
              ";3:" + str(chipnum) + ";4:" + str(self._ch) + ";5:" + data_filters
        return msg

    def start(self):
        _context = zmq.Context()
        _controller = _context.socket(zmq.REQ)
        _controller.connect("tcp://localhost:22720")
        msg = self.__encode();
        _controller.send(msg)
        msg = _controller.recv()