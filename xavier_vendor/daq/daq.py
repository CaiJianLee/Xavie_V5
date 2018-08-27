import sys
from acquisitor import DataAcquisitor
from acquisitor import DataAcquisitorEx
from channel import DataChannel
from channel import DataChannelEx
import data_filter as Filter
from ee.common import logger
from ee.common import utility
from ee.common import daemon
from ee.common import xavier as Xavier

data_channels = {}
channel_name = []
high_speed_flag = False

def _get_board_channel():
    channel_list = []
    boards = Xavier.call("get_boards")
    for board in boards.values():
        if 'daq_channel' in board.keys():
            for channel in board['daq_channel']:
                channel_list.append(channel)
    return channel_list

def get_channel(channel_name):
    global data_channels
    if channel_name in data_channels.keys():
        return data_channels[channel_name]
    else:
        logger.warning("the %s channel does not  exist"%(channel_name))
        return False

def create_all_channel():
    global data_channels
    try:
        board_channels = _get_board_channel()
        logger.boot("board channels %r"%(board_channels))
        for channel in board_channels:
            name = channel['id']

            data_filters = []
            for data_filter in channel['filters']:
                if high_speed_flag == True:
                    data_filters.append(data_filter)
                else:
                    data_filters.append(getattr(Filter,data_filter))
            sub_filters = []
            frame_type = int(channel['frame_type'],16)
            if True == isinstance(channel['chipnum'], int):
                sub_filter = {"type": frame_type, "chipnum": channel['chipnum']}
                sub_filters.append(sub_filter)
            elif True == isinstance(channel['chipnum'], list):
                for i in range(0, len(channel['chipnum'])):
                    sub_filter = {"type": frame_type, "chipnum": channel['chipnum'][i]}
                    sub_filters.append(sub_filter)
            else:
                logger.error("%s channel chipnum type invalue"%(name))
                continue
            if high_speed_flag == True:
                data_channels[name] = DataChannelEx(name, channel['port'], channel['ch'], sub_filters, data_filters)
            else:
                data_channels[name] = DataChannel(name, channel['port'], channel['ch'], sub_filters, data_filters)
            channel_name.append(name)
    except Exception as e:
        logger.error("create channel %r fail: %s"%(channel, repr(e)))
        return False
    else:
        return True

def run_all_channel():
    global data_channels
    channels = []

    try:
        for name, channel in data_channels.iteritems():
            channel.start()
            channels.append(channel)
    except Exception as e:
        logger.error("run the %s channel fail: %s"%(name, repr(e)))
    if high_speed_flag == False:
        for channel in channels:
            channel.join()

if __name__ == '__main__':
    utility.register_signal_handle()
    # set daemon 
    daq_daemon = daemon.Daemon("daq")
    daq_daemon.start()

    logger.init("daq.log")
    logger.setLevel('WARNING')

    len_args = len(sys.argv)
    if (len_args < 2):
        dma_path = "/dev/AXI4_DMA"
    elif (len_args < 3):
        dma_path = sys.argv[1]
    else:
        dma_path = sys.argv[1]
        if sys.argv[2] == "high_speed":
            high_speed_flag = True

    logger.boot("the dma path is %s" %(dma_path))

    if high_speed_flag == True:
        data_acquisitor = DataAcquisitorEx(dma_path)
    else:
        data_acquisitor = DataAcquisitor(dma_path)
    data_acquisitor.start()

    ''' add debug channel '''
    debug_sub_filters = [{"type":"all", "chipnum":"all"}]
    if high_speed_flag == True:
        debug_data_filters = ["sg_output_filter"]
        debug_channel = DataChannelEx("debug", 22710, 255, debug_sub_filters, debug_data_filters)
    else:
        debug_data_filters = [Filter.output]
        debug_channel = DataChannel("debug", 22710, 255, debug_sub_filters, debug_data_filters)
    debug_channel.start()

    # Create all channel in the profile by default filter 
    if create_all_channel() == True:
        # If you need to change the filter, get the channel by name and change it here.
        # For example:
        # channel = get_channel('volt')
        # data_filters = [Filter.check, Filter.output]
        # data_filters = [Filter.divide_datalogger_channel, Filter.output]

        run_all_channel()
