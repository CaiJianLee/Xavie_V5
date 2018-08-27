import logging
import logging.handlers
import os
import sys
import random
import time
import inspect
import datetime
import re
import threading
import fcntl
import select
import ctypes
import traceback
import socket
import zmq
import json
from functools import wraps
from ee.common import utility

mutex = threading.Lock()
libsys = ctypes.CDLL("libc.so.6")
READ_ONLY = (select.EPOLLIN | select.EPOLLHUP | select.EPOLLPRI | select.EPOLLERR)
READ_WRITE = (READ_ONLY | select.EPOLLOUT)
TRANSPORT = 22739

(r,w) = os.pipe()
pipe_w = os.fdopen(w, "w")
pipe_r = os.fdopen(r, "r")

MAX_SIZE = 1024 * 1024 * 10

BOOT = logging.CRITICAL
CRITICAL = logging.CRITICAL
ERROR    = logging.ERROR
WARNING  = logging.WARNING
INFO     = logging.INFO
DEBUG    = logging.DEBUG
NOTSET   = logging.NOTSET

loc_lev = {'CRITICAL':CRITICAL, 'ERROR':ERROR, 'WARNING':WARNING, 'INFO':INFO, 'DEBUG':DEBUG, 'BOOT':BOOT}
name_lev = {'boot':'[BOOT ]', 'debug': '[DEBUG]', 'info': '[INFO ]', 'warning':'[WARN ]', 'error':'[ERROR]', 'critical':'[CRIT ]'}
thread_local = threading.local()
log_object = {}


class LogEnv(threading.Thread):
    def __init__(self, file_name):
        super(LogEnv, self).__init__()
        self._forever = True
        self.file_name = file_name
        self.local_name = (file_name.split(".log")[0]).upper()


    def __run(self):
        '''
        msg format:
        {
            "name":{
                "locallevel":"<level>",
                "uploadlevel":"<level>",
                "upload":True/False
            }
        }
        '''
        self._context = zmq.Context()
        subscriber = self._context.socket(zmq.SUB)
        subscriber.connect("tcp://localhost:22730")
        subscriber.setsockopt(zmq.SUBSCRIBE, "")

        poller = zmq.Poller()
        self._poller = poller
        poller.register(subscriber, zmq.POLLIN)

        while self._forever:
            socks = dict(poller.poll())
            if subscriber in socks:
                try:
                    value = subscriber.recv()
                except zmq.ZMQError, e:
                    if e.errno == zmq.ETERM:
                        break
                    else:
                        pass
                msg = json.loads(value)

                try:
                    for key in msg.keys():
                        _env_key = 'XAVIER_LOG_' + key.upper()
                        if os.getenv(_env_key):
                            try:
                                _env = json.loads(os.environ[_env_key])
                            except Exception:
                                _env = {}
                        else:
                            _env = {}
                            os.putenv(_env_key, "")
                        if msg[key].has_key("locallevel") and msg[key]["locallevel"].upper() in loc_lev:
                            level = msg[key]["locallevel"].upper()
                            if log_object.has_key(key):
                                log_object[key].local_level = loc_lev[level]
                                log_object[key].logger.setLevel(log_object[key].local_level)
                            _env["locallevel"] = msg[key]["locallevel"]

                        if msg[key].has_key("uploadlevel") and msg[key]["uploadlevel"].upper() in loc_lev:
                            level = msg[key]["uploadlevel"].upper()
                            if log_object.has_key(key):
                                log_object[key].upload_level = loc_lev[level]
                            _env["uploadlevel"] = msg[key]["uploadlevel"]

                        if msg[key].has_key("upload") and bool == type(msg[key]["upload"]):
                            if log_object.has_key(key):
                                log_object[key].upload = msg[key]["upload"]
                            _env["upload"] = msg[key]["upload"]
                        os.environ[_env_key] = json.dumps(_env)
                except:
                    warning(traceback.format_exc())

    def run(self):
        thread_local.file = self.file_name
        thread_local.name = self.local_name
        try:
            self.__run()
        except:
            warning(traceback.format_exc())

    def stop(self):
        self._forever = False


class ScreenPrintLog(threading.Thread):
    def __init__(self, file_name):
        super(ScreenPrintLog, self).__init__()
        self.file_name = file_name
        self.local_name = (file_name.split(".log")[0]).upper()

    def run(self):
        thread_local.file = self.file_name
        thread_local.name = self.local_name
        epoll = select.epoll()
        epoll.register(pipe_r.fileno(), READ_ONLY)
        while True:
            try:
                events = epoll.poll()
            except IOError:
                continue
            for fileno, event in events:
                try:
                    if (event & (select.POLLIN | select.POLLPRI)):
                        self._screen_log()
                except Exception as e:
                    pass
        return True

    def _screen_log(self):
        while True:
            try:
                log_str = pipe_r.readline().strip()
                if log_str:
                    warning(log_str)
            except Exception:
                break
            log_str = ""
        return None


class SmartGiantLog():
    def __init__(self, file_name):
        self.file = file_name
        self.name = (file_name.split(".log")[0]).upper()
        self.logger = None
        self.local_level = None
        self.upload_level = None
        self.upload = False
        self.trans = None
        self.local_env = None
        self.log_path = None
        self.log_server = None
        self.log_count = None
        self.handle = None
        self.trace = False
        self.format = '%Y-%m-%d %H:%M:%S'

    def create_log_handle(self):
        self.local_env = "XAVIER_LOG_" + self.name
        if os.environ.has_key(self.local_env) and os.environ[self.local_env]:
            self._init_value_from_env()

        self.logger = logging.getLogger(self.name)

        self.log_path = utility.get_log_path()
        if (False == os.path.exists(self.log_path)):
            os.system("mkdir %s -p >/dev/null"%(self.log_path))

        self.log_count = self._get_log_count(self.file)
        self.handle = logging.handlers.RotatingFileHandler("%s/%s"%(self.log_path, self.file), maxBytes = MAX_SIZE, backupCount = 10)
        #self.handle.setFormatter(format)
        self.handle.setLevel(NOTSET)
        self.logger.addHandler(self.handle)
        if None == self.local_level:
            self.local_level = WARNING
        self.logger.setLevel(self.local_level)
        self.log_server = ScreenPrintLog(self.file)
        self.log_server.setDaemon(True)
        self.log_server.start()
        if True == self.upload:
            self.connect_logupload()

    def _init_value_from_env(self):
        _env = json.loads(os.environ[self.local_env])

        if _env.has_key("locallevel") and _env["locallevel"].upper() in loc_lev:
            if True == isinstance(_env["locallevel"], str) or unicode == type(_env["locallevel"]):
                self.local_level = loc_lev[_env["locallevel"].upper()]

        if _env.has_key("uploadlevel") and _env["uploadlevel"].upper() in loc_lev:
            if True == isinstance(_env["uploadlevel"], str) or unicode == type(_env["uploadlevel"]):
                self.upload_level = loc_lev[_env["uploadlevel"].upper()]

        if _env.has_key("upload") and bool == type(_env["upload"]):
            self.upload = _env["upload"]

    def reset_log_handle(self):
        self.logger.removeHandler(self.handle)
        self.handle = logging.FileHandler("%s/%s"%(self.log_path, self.file))
        self.handle.setLevel(NOTSET)
        self.logger.addHandler(self.handle)

    def _dump_log(self):
        mutex.acquire(1)
        try:
            file = "%s/%s.10"%(self.log_path, self.file)
            if False == os.path.exists(file):
                mutex.release()
                return None
            back_path = self.log_path + "/back"
            if False == os.path.exists(back_path):
                os.system("mkdir %s -p >/dev/null"%(back_path))

            if self.log_count > 9:
                self.log_count = 0
            back_file = "%s/%s.*"%(back_path, self.file)
            tar_name = "%s/%s%02d.tar.gz"%(back_path, self.name.lower(), self.log_count)
            os.system("rm -f %s >/dev/null"%(back_file))
            os.system("rm -f %s >/dev/null"%(tar_name))
            os.system("mv %s/%s.* %s/ >/dev/null"%(self.log_path, self.file, back_path))
            os.system("tar -cvzf %s %s/%s.*>/dev/null"%(tar_name, back_path, self.file))
            os.system("rm -f %s >/dev/null"%(back_file))
        except Exception:
            pass
        self.log_count += 1
        mutex.release()
        return None

    def _get_log_level(self, env_value):
        for i in range(0, len(env_value)):
            try:
                return loc_lev[env_value[i]]
            except Exception:
                pass
        return self.local_level

    def set_path(self, path):
        if False == os.path.exists(path):
            os.system("mkdir %s -p >/dev/null"%(path))
        self.log_path = path
        self.reset_log_handle()

    def _get_log_count(self, file_name):
        last_time = 0
        last_count = 0
        back_path = self.log_path + "/back"
        if False == os.path.exists(back_path):
            os.system("mkdir %s -p >/dev/null"%(back_path))
            return 0

        for i in range(0, 10):
            name = ("%s/%s%02d.tar.gz"%(back_path, self.name.lower(), i))
            if False == os.path.exists(name):
                return i
            _time = os.path.getmtime(name)
            if last_time < _time:
                last_time = _time
                last_count = i
        return last_count + 1

    def connect_logupload(self):
        if self.trans:
            self.trans.close()

        HOST = "0.0.0.0"
        PORT = TRANSPORT
        trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            trans.connect((HOST, PORT))
        except socket.error:
            #warning("connect %s:%s failed, please check log upload module started!!"%(HOST, PORT))
            return False

        trans.send(";;register_logger;;%s;;"%(self.name.lower()))
        res = trans.recv(32)
        if not "True" == res:
            return False

        self.trans = trans
        return True

def log_decorator(fn):
    @wraps(fn)
    def wraps_wrapper(msg, *args, **kwargs):
        try:
            if True == log_object[thread_local.name].trace:
                frame = sys._getframe(1)
                msg = str(frame.f_code) + str(msg)

            name = fn.__name__
            msg = '[' + datetime.datetime.now().strftime(log_object[thread_local.name].format) + ']' \
                   + "[LWP:%d]"%(libsys.syscall(224)) + name_lev[name] + str(msg)
            try:
                if True == log_object[thread_local.name].upload:
                    lv = None
                    if log_object[thread_local.name].upload_level:
                        lv = log_object[thread_local.name].upload_level
                    else:
                        lv = log_object[thread_local.name].local_level
                    if loc_lev[name.upper()] == lv or loc_lev[name.upper()] > lv:
                        if not log_object[thread_local.name].trans:
                            if True == log_object[thread_local.name].connect_logupload():
                                log_object[thread_local.name].trans.send(msg)
                        else:
                            log_object[thread_local.name].trans.send(msg + '\r\n')
            except socket.error:
                try:
                    log_object[thread_local.name].trans.close()
                except Exception:
                    pass
                log_object[thread_local.name].trans = None
            except KeyError:
                pass

            result = fn(msg, *args, **kwargs)
            log_object[thread_local.name]._dump_log()
            return result
        except Exception as e:
            pass

    return wraps_wrapper

def init(file_name):
    thread_local.name = (file_name.split(".log")[0]).upper()
    mutex.acquire(1)
    try:
        type(log_object[thread_local.name])
        mutex.release()
        return None
    except Exception:
        pass
    try:
        log_object[thread_local.name] = SmartGiantLog(file_name)
    except Exception as e:
        mutex.release()
        return
    mutex.release()
    le = LogEnv(file_name)
    le.setDaemon(True)
    le.start()
    time.sleep(0.001)
    log_object[thread_local.name].create_log_handle()
    start_msg = "\r\n\r\n\r\n| %s | \r\n| %s |\r\n| %s |\r\n\r\n"\
                %("".center(61, '-'), (thread_local.name + " Start").center(61, '*'), "".center(61, '-'))
    boot(start_msg)
    return None

@log_decorator
def boot(msg, *args, **kwargs):
    try:
        log_object[thread_local.name].logger.critical(msg, *args, **kwargs)
    except Exception as e:
        pass
    return None

@log_decorator
def info(msg, *args, **kwargs):
    try:
        log_object[thread_local.name].logger.info(msg, *args, **kwargs)
    except Exception as e:
        pass
    return None

@log_decorator
def warning(msg, *args, **kwargs):
    try:
        log_object[thread_local.name].logger.warning(msg, *args, **kwargs)
    except Exception as e:
        pass
    return None

@log_decorator
def error(msg, *args, **kwargs):
    try:
        log_object[thread_local.name].logger.error(msg, *args, **kwargs)
    except Exception as e:
        pass
    return None

@log_decorator
def critical(msg, *args, **kwargs):
    try:
        log_object[thread_local.name].logger.critical(msg, *args, **kwargs)
    except Exception as e:
        pass
    return None

@log_decorator
def debug(msg, *args, **kwargs):
    try:
        log_object[thread_local.name].logger.debug(msg, *args, **kwargs)
    except Exception as e:
        pass
    return None

def setLevel(level):
    try:
        if (True == isinstance(level, int)):
            log_object[thread_local.name].local_level = level
        else:
            log_object[thread_local.name].local_level = loc_lev[level.upper()]
        log_object[thread_local.name].logger.setLevel(log_object[thread_local.name].local_level)
    except Exception:
            pass
    return None

def setLogPath(path):
    if (True == isinstance(path, str)):
        try:
            log_object[thread_local.name].set_path(path)
        except Exception:
            pass

def print_list2hex(data):
    if isinstance(data, list):
        out_data = '['
        for x in data:
            if isinstance(x, int):
                out_data += '%#x, '%x
            elif isinstance(x, list):
                out_data += '%s, '%print_list2hex(x)
            else:
                out_data += '%s, '%x
        out_data = out_data[:-2] + ']'
    else:
        out_data = data
    return out_data