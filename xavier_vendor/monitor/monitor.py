import os
import sys
import zmq
import json
import subprocess
import time
import traceback
import collections
import errno
import signal
from functools import wraps
from threading import Thread
from ee.common import daemon
from ee.common import logger
from ee.common import utility

monitor_json = collections.OrderedDict()

class MonitorServer(Thread):

    def __init__(self):
        super(MonitorServer, self).__init__()

    def _run(self):
        context = zmq.Context()
        reply = context.socket(zmq.REP)
        reply.bind("tcp://*:7611")
        while True:
            message = reply.recv()
            if message:
                msg_list = message.split(" ")
                if msg_list[0] == "UndoMonitor":
                    monitor_json[key]["monitor"] = 2
            reply.send("")

    def run(self):
        while True:
            try:
                self._run()
            except Exception as e:
                logger.warning("MonitorServer except:%s"%(repr(e)))

class TimeoutError(Exception):
    pass


class LogUploadEnv():
    def __init__(self, file):
        self._file = file
        self._config = {}

    def load_config(self):
        _config = utility.load_json_file(self._file)
        for key in _config:
            if ";;log_config" == key:
                self._config = _config[key]
        return None

    def _set_env(self):
        self.load_config()
        for key in self._config:
            if self._config[key].has_key("port") and len(self._config[key]) > 1:
                _env_key = 'XAVIER_LOG_' + (key.split(".log")[0]).upper()
                _env = self._config[key]
                del _env["port"]
                if _env.has_key("level"):
                    _level = _env["level"]
                    if _level.upper() in logger.loc_lev:
                        _env["uploadlevel"] = _level.upper()
                    del _env["level"]
                os.putenv(_env_key, "")
                os.environ[_env_key] = json.dumps(_env)
        return None


def result_timeout(seconds=5, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            result = func(*args, **kwargs)
            signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator

@result_timeout(2)
def get_result(result):
    if result is None:
        return (None, None)
    try:
        strout, strerr = result.communicate()
    except Exception:
        return (None, None)
    return (strout, strerr)


def _load_monitor_json():
    load_json = utility.load_json_file("/opt/seeing/app/monitor/monitor.json")
    order_dict = {}
    for key in load_json:
        if len(key) > 2 and ";;" == key[0:2]:
            continue
        order_dict[key] = load_json[key]["order"]
    order_list = sorted(order_dict.iteritems(), key=lambda a:a[1])
    for order in order_list:
        monitor_json[order[0]] = load_json[order[0]]

def main():
    _load_monitor_json()
    while True:
        for key in monitor_json:
            result = subprocess.Popen("ps -aux | awk '{print $11}' | grep ^%s$"%(key), shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            strout, strerr = get_result(result)
            if strout.strip() == key:
                if monitor_json[key]["mode"].strip() == "only_monitor":
                    monitor_json[key]["mode"] = "start_monitor"

            elif monitor_json[key]["mode"].strip() == "start_monitor":
                result = subprocess.Popen("%s"%(monitor_json[key]["start"]), shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                strout, strerr = get_result(result)
                if strerr:
                    logger.error("start %s module failed:%s"%(key, strerr))
                else:
                    logger.warning("start %s module"%(key))
                if "delay" in monitor_json[key]:
                    time.sleep(float(monitor_json[key]["delay"])/1000)

            elif monitor_json[key]["mode"].strip() == "only_start":
                result = subprocess.Popen("%s"%(monitor_json[key]["start"] ), shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                strout, strerr = get_result(result)
                if strerr:
                    logger.error("start %s module failed:%s"%(key, strerr))
                else:
                    logger.warning("start %s module"%(key))
                if "delay" in monitor_json[key]:
                    time.sleep(float(monitor_json[key]["delay"])/1000)
                monitor_json[key]["mode"] = "started"

            elif monitor_json[key]["mode"].strip() == "close_monitor":
                monitor_json[key]["mode"] = "only_monitor"

        time.sleep(0.5)

if __name__ == "__main__":
    utility.register_signal_handle()

    # set daemon 
    _daemon = daemon.Daemon("monitor")
    _daemon.start()

    _env = LogUploadEnv(utility.get_app_path()+"/monitor/monitor.json")
    _env._set_env()
    logger.init("monitor.log")
    #th = MonitorServer()
    #th.start()
    while True:
        try:
            main()
        except Exception as e:
            logger.warning("monitor module except : %s"%(repr(e)))
