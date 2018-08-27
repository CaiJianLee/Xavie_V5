import re
import command.server.handle_utility as Utility
from ee.common import xavier as Xavier
from ee.common import logger

global freq_board_name
freq_board_name = "freq"

@Utility.timeout(5)
def frequency_measure_handle(params):

    help_info = "frequency measure(<vref>,<measure_time>)\r\n\
\tvref: () mV, float data $\r\n\
\tmeasure_time: ()ms, float data $\r\n\
"

    ''' help '''
    if Utility.is_ask_for_help(params) is True:
        return Utility.handle_done(help_info)

    ''' parameters analysis '''
    params_count = len(params)
    if params_count  != 2:
        return Utility.handle_error(Utility.handle_errorno['handle_errno_parameter_invalid'],"param length error")

    vref = float(params[0])
    time = int(params[1])
    vref = (vref,'mV')
    measure_time = (time, 'ms')

    #doing
    global freq_board_name
    result = Xavier.call('eval',freq_board_name,'frequency_measure', vref, measure_time)

    if result is False:
        return Utility.handle_done("-1.000000 Hz")

    out_msg = '%f %s'%(result['freq'][0],result['freq'][1])
    return Utility.handle_done(out_msg)
