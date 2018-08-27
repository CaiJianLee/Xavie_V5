# -*- coding:utf-8 -*-
import os
import re
import sys
import json
import zmq
import errno
import signal
from functools import wraps
from ee.common import xavier

handle_errorno = {
    #校验不过(error: the CRC)
    'handle_errno_crc_checksum_failure':-67, \
    #无权限(error: the instruction need permissions)
    'handle_errno_no_permission':-68, \
    #/任务正在运行(error: the instruction also is doing.which need long time)
    'handle_errno_running':-69, \
    'handle_errno_devices_error':-70, \
    'handle_errno_time_out':-75, \
    'handle_errno_call_handle_exception':-76, \
    'handle_errno_not_have_this_command':-190,\
    #参数出错-193...-223：参数\参数1...参数30错误
    'handle_errno_parameter_invalid':-193, \
    #执行出错-224...-254：执行\执行1...执行30错误(error: casued by ARM board doing)
    'handle_errno_execute_failure':-224,
    }

def handle_done(backstring = ""):
    sResult = "Done"
    sResult += backstring
    return sResult

def handle_error(errorno,backstring = ""):
    sResult = "Error"
    sResult += str(errorno)
    sResult += " "
    sResult += backstring
    return sResult

def is_ask_for_help(params):
    if len(params) == 1 and params[0] == "?":
        return True
    else :
        return False

class TimeoutError(Exception):
    pass

def timeout(seconds=5, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            except TimeoutError:
                try:
                    xavier.proxy.reconnect()
                except Exception:
                    pass
                result = handle_error(handle_errorno["handle_errno_time_out"], "call handle timeout")
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
