
import sys
import os
from command.server import handler
from command.server import epoll_server
from ee.common import logger
from ee.common import utility
from ee.common import daemon

channel_path = "/opt/seeing/dut_firmware/ch9"

if __name__ == "__main__":
    if (os.path.isdir(channel_path)) == False:
        os.mkdir(channel_path)
    
    utility.register_signal_handle()
    # set daemon 
    cmd_daemon = daemon.Daemon("fwdl9")
    cmd_daemon.start()
    
    logger.init("fwdl9.log")
    logger.setLevel('INFO')
    
    arg_len = len(sys.argv)
    for i in range(1, arg_len):
        epoll_server.create_srv(sys.argv[i])
    if arg_len > 1:
        handler.handle_init()
        epoll_server.run_server()
    os._exit(0)