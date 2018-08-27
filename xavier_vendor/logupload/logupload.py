import os
import socket
import select
import ctypes
import time
import traceback
import collections
from threading import Thread
from ee.common import utility
from ee.common import logger
from ee.common import daemon

READ_ONLY = (select.EPOLLIN | select.EPOLLHUP | select.EPOLLPRI | select.EPOLLERR)
READ_WRITE = (READ_ONLY | select.EPOLLOUT)

TRANSPORT = 22739
name_lev = {'boot':'[BOOT ]', 'info': '[INFO ]', 'warning':'[WARN ]', 'error':'[ERROR]', 'critical':'[CRIT ]'}


class LogUpload(Thread):
    def __init__(self, log="logupload.log", config_file=utility.get_app_path()+"/monitor/monitor.json"):
        super(LogUpload, self).__init__()
        self._forever = True
        self._file = config_file
        self._config = collections.OrderedDict()
        self._servers = {}
        self._log = log

    def _load_log_config(self):
        _config = utility.load_json_file(self._file, object_pairs_hook=collections.OrderedDict)
        for key in _config:
            if ";;log_config" == key:
                for k in _config[key]:
                    _ = k.split(".log")[0]
                    self._config[_] = _config[key][k]

    def _create_servers(self):
        '''
        create log upload servers
        '''
        self._load_log_config()
        for key in self._config:
            _exist = False
            for k in self._servers:
                if self._config[key]["port"] == self._servers[k].getsockname()[1]:
                    self._servers[key] = self._servers[k]
                    _exist = True
                    break
            if True == _exist:
                continue

            HOST = "0.0.0.0"
            PORT = self._config[key]["port"]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((HOST, PORT))
            sock.listen(100)
            self._servers[key] = sock

    def __run(self):
        connections = {}
        loggers = {}
        requests = {}
        servers = {}
        clients = {}

        self._create_servers()

        '''
        22739 is log trans port
        '''
        HOST = "0.0.0.0"
        PORT = TRANSPORT
        trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        trans.setblocking(False)
        trans.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        trans.bind((HOST, PORT))
        trans.listen(100)

        epoll = select.epoll()
        epoll.register(trans.fileno(), READ_ONLY)
        for key in self._servers:
            try:
                epoll.register(self._servers[key].fileno(), READ_ONLY)
            except IOError:
                pass
            servers[self._servers[key].fileno()] = self._servers[key]

        while self._forever:
            try:
                events = epoll.poll()
            except Exception:
                continue
            for fileno, event in events:
                if (event & (select.POLLIN | select.POLLPRI)) :
                    # POLLIN
                    if fileno in servers:
                        # accept clients connection
                        connection, addr = servers[fileno].accept()
                        connection.setblocking(False)
                        epoll.register(connection.fileno(), READ_ONLY)

                        if clients.has_key(fileno):
                            epoll.unregister(clients[fileno].fileno())
                            del connections[clients[fileno].fileno()]
                            clients[fileno].close()
                            del clients[fileno]

                        clients[fileno] = connection
                        connections[connection.fileno()] = connection
                        print(connection.getpeername())
                    elif fileno == trans.fileno():
                        # log module register
                        _logger, addr = trans.accept()
                        _logger.setblocking(False)
                        epoll.register(_logger.fileno(), READ_ONLY)
                        _ = {"name":"", "sock":_logger}
                        loggers[_logger.fileno()] = _
                        requests[_logger.fileno()] = ""
                    elif fileno in connections:
                        # recv clients msg:
                        # msg is null, means clients close socket
                        # msg not null, recv and drop it
                        msgs = ""
                        while True:
                            try:
                                msg = connections[fileno].recv(1024)
                            except Exception as e:
                                # recv over
                                break
                            else:
                                if not msg:
                                    # connect off
                                    break
                            msgs = msgs + msg

                        if not msgs:
                            # connect off
                            keys = clients.keys()
                            for k in keys:
                                if clients[k].fileno() == fileno:
                                    del clients[k]
                                    break
                            epoll.unregister(fileno)
                            connections[fileno].close()
                            del connections[fileno]
                        else:
                            epoll.modify(fileno, READ_WRITE)
                    elif fileno in loggers:
                        # recv logs
                        # msg is null, means log close socket
                        # msg not null, recv it
                        msgs = ""
                        while True:
                            try:
                                msg = loggers[fileno]["sock"].recv(2048)
                            except Exception as e:
                                # recv over
                                break
                            else:
                                if not msg:
                                    # connect off
                                    break
                            msgs = msgs + msg
                        if not msgs:
                            epoll.unregister(fileno)
                            loggers[fileno]["sock"].close()
                            del loggers[fileno]
                        else:
                            requests[fileno] = requests[fileno] + msgs
                            epoll.modify(fileno, READ_WRITE)
                elif (event & select.EPOLLOUT):
                    if fileno in connections:
                        epoll.modify(fileno, READ_ONLY)
                    elif fileno in loggers:
                        if "" == loggers[fileno]["name"]:
                            # get module
                            if ";;register_logger;;" in requests[fileno]:
                                module = requests[fileno].split(";;register_logger;;")[1]
                                if module and ";;" in module:
                                    name = module.split(";;")[0].lower()
                                    if name in self._config:
                                        loggers[fileno]["name"] = name
                                        requests[fileno] = ""
                                        loggers[fileno]["sock"].send("True")
                                    else:
                                        requests[fileno] = ""
                                        loggers[fileno]["sock"].send("False")
                                epoll.modify(fileno, READ_ONLY)
                            else:
                                requests[fileno] = ""
                                epoll.modify(fileno, READ_ONLY)
                        else:
                            # send to clients
                            name = loggers[fileno]["name"]
                            key = self._servers[name].fileno()
                            if clients.has_key(key):
                                clients[key].send(requests[fileno])
                            requests[fileno] = ""
                            epoll.modify(fileno, READ_ONLY)
                elif (event & select.EPOLLHUP):
                    if fileno in connections:
                        keys = clients.keys()
                        for k in keys:
                            if clients[k].fileno() == fileno:
                                del clients[k]
                                break
                        epoll.unregister(fileno)
                        connections[fileno].close()
                        del connections[fileno]
                    elif fileno in loggers:
                        epoll.unregister(fileno)
                        loggers[fileno]["sock"].close()
                        del loggers[fileno]

    def run(self):
        try:
            if self._log:
                logger.init(self._log)
            self.__run()
        except Exception:
            logger.warning(traceback.format_exc())
            return None

    def stop(self):
        self._forever = False
        return None


if __name__ == "__main__":
    logupload_daemon = daemon.Daemon("logupload", stdout=os.devnull, stderr=os.devnull)
    logupload_daemon.start()
    logger.init("logupload.log")
    lu = LogUpload()
    lu.start()
    lu.join()
