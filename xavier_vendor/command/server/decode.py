from ctypes import *
import platform
import re
import os
from ee.common import utility

cmd_so = utility.get_lib_path() + "/libsgcmd.so"
libcmd = cdll.LoadLibrary(cmd_so)

CONFIG_TERMINAL_COMMANDID_LENGTH = 16
CONFIG_TERMINAL_COMMAND_LENGTH = 64
CONFIG_TERMINAL_CMDPARAMETER_LENGTH = 1024
CONFIG_TERMINAL_REPLY_LENGTH = 4096
CONFIG_TERMINAL_RECV_LENGTH = 2048

class SeTimestamp(Structure):
    _fields_ = [('SeTimeMiliSecods', c_ushort), ('SeTimeSeconds', c_uint)]


class SeCommandCustomField(Structure):
    _fields_ = [('nOperation', c_int), ('sCommandID', c_char * CONFIG_TERMINAL_COMMANDID_LENGTH),                                                  \
               	('sCommandKeyword', c_char * CONFIG_TERMINAL_COMMAND_LENGTH), ('sCommandParameters', c_char * CONFIG_TERMINAL_CMDPARAMETER_LENGTH),\
                ('sCommandReply', c_char_p), ('nCommandReplyBuffLen', c_short), ('nCommandReplySize', c_short),                                    \
                ('tRequestTime', SeTimestamp), ('nStatus', c_int),                                                                                 \
                ('nErrorNO', c_int)]

class SeNetWorkCustomRecv(Structure):
    _fields_ = [('nRecvBufferSize', c_ushort), ('iRecvBufferTailCursor', c_int),
                ('iRecvBufferCurrentCursor', c_int), ('sRecvBuffer', c_char * CONFIG_TERMINAL_RECV_LENGTH)]


libcmd.sg_cmd_decode.restype = SeCommandCustomField
decode_command = SeCommandCustomField()

def sg_decode(args):
    return libcmd.sg_cmd_decode(args)

def sg_send(fileno, string, size_t):
    return libcmd.sg_send(fileno, string, size_t)

def sg_call_result(decode_command, result, result_len):
    return libcmd.sg_cmd_call_result(decode_command, result, result_len)

def sg_get_cmd(arg):
    return libcmd.sg_get_complete_cmd(arg)

def sg_recv(sock, arg):
    return libcmd.sg_recv(sock, arg)

def sg_network_init(arg):
    libcmd.sg_netword_init(arg)
    return None

def sg_destroy_result(decode_command):
    return libcmd.sg_cmd_destroy_result(decode_command)
