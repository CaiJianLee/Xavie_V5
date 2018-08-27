
import re
import time
import sys
import command.server.handle_utility as Utility
from ee.common import logger
from collections import OrderedDict

from ee.common import xavier as Xavier1
sys.path.append('/opt/seeing/app/')
from b31_bp import xavier1 as Xavier2

global agv
agv=sys.argv[1]
Xavier=Xavier1
xavier_module = {"tcp:7801":Xavier1, "tcp:7802":Xavier2}
if agv in xavier_module:
    Xavier=xavier_module[agv]
    

test_base_board_name = "zynq"

def temperature_read_handle(params):
    help_info = "temperature read()$\r\n"   

    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ret=Xavier.call("eval",test_base_board_name,"temperature_read")

    return Utility.handle_done("%s"%(str(ret)))