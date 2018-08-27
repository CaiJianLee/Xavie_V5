from __future__ import division
import time
from ee.bus.axi4lite import Axi4lite
from ee.common.data_operate import DataOperate
from ee.common import logger

class Axi4AidMaster():
    
    def __init__(self,name):
        self.name = name
        self.reg_num = 8192
        self.__axi4lite=Axi4lite(self.name,self.reg_num)
        if self.__axi4lite.open() is False:
            logger.error('open %s device register number %d fail'%(self.name, self.reg_num))
        self.__data_deal = DataOperate()
        
    def enable(self):
        """Enable this FPGA function"""
        self.__axi4lite.write(0x10,[0x01],1)
        return None
        
    def disable(self):
        """Disable this FPGA function"""
        self.__axi4lite.write(0x10,[0x00],1)
        return None

    def aid_switch_on(self):
        """Release aid bus, allow aid communication"""
        # 0x11 [0]--vdg_switch; [4]--vdg_poll_en
        rd_data = self.__axi4lite.read(0x11,1)
        rd_data[0] = rd_data[0] & 0xFE;
        self.__axi4lite.write(0x11, rd_data, 1)
        return None
        
    def aid_switch_off(self):
        """Force the aid bus to be low level, forbade aid communication"""
        # 0x11 [0]--vdg_switch; [4]--vdg_poll_en
        rd_data = self.__axi4lite.read(0x11,1)
        rd_data[0] = rd_data[0] | 0x01;
        self.__axi4lite.write(0x11, rd_data, 1)
        return None
        
    def aid_detect_poll_on(self):
        """enable aid detect poll mode, that is the 70ms loop sends a "74 00 01" request command(otpID)"""
        # 0x11 [0]--vdg_switch; [4]--vdg_poll_en
        rd_data = self.__axi4lite.read(0x11,1)
        rd_data[0] = rd_data[0] | 0x10;
        self.__axi4lite.write(0x11, rd_data, 1)
        return None
        
    def aid_detect_poll_off(self):
        """disable aid detect poll mode"""
        # 0x11 [0]--vdg_switch; [4]--vdg_poll_en
        rd_data = self.__axi4lite.read(0x11,1)
        rd_data[0] = rd_data[0] & 0xEF;
        self.__axi4lite.write(0x11, rd_data, 1)
        return None

    def aid_cmd(self,cmd_req_data):
        """ signal aid cmd communication
            
            Args:
                cmd_req_data(list): aid request command data(except CRC data),len 1~512

            Returns:
                aid_resp_data(list): aid response command data(include CRC data),len 0~512(len=0 --> no aid response data)
        """
        # ctrl reg cfg
        # 0x10 [0]--module_en
        # 0x11 [0]--vdg_switch; [4]--vdg_poll_en
        # 0x12 [0]--start
        # 0x13 [0]--state
        # 0x20~0x21 aid_req_len
        # 0x22~0x23 aid_resp_len
        # 0x24~0x27 aid_rece_timeout_cnt
        # 0x80 wr--wr_req_data; rd--rd_resp_data
        # wait detect poll over
        rd_data = self.__axi4lite.read(0x11,1)
        vdg_poll_en_flag = (rd_data[0] & 0x10) >> 4
        if(vdg_poll_en_flag == 0x01):
            rd_data[0] = rd_data[0] & 0xEF;
            self.__axi4lite.write(0x11, rd_data, 1)
            timeout_cnt = 0;
            rd_data = self.__axi4lite.read(0x13,1)
            while (rd_data[0] == 0x00) and timeout_cnt < 1000:
                time.sleep(0.001)
                rd_data = self.__axi4lite.read(0x13,1)
                timeout_cnt = timeout_cnt + 1
            if(timeout_cnt == 1000):
                logger.error('wait poll detct timeout')
                return False    
        # cfg req len
        aid_req_len = len(cmd_req_data)
        wr_data = self.__data_deal.int_2_list(aid_req_len, 2)
        self.__axi4lite.write(0x20, wr_data, len(wr_data))
        # wr cmd_req_data to req_fifo
        self.__axi4lite.write_array(0x80, cmd_req_data, aid_req_len, 8)
        # start aid communication
        self.__axi4lite.write(0x12, [0x01], 1)
        # query state
        timeout_cnt = 0;
        rd_data = self.__axi4lite.read(0x13,1)
        while (rd_data[0] == 0x00) and timeout_cnt < 10000:
            time.sleep(0.001)
            rd_data = self.__axi4lite.read(0x13,1)
            timeout_cnt = timeout_cnt + 1
        if(timeout_cnt == 10000):
            logger.error('aid communication timeout')
            return False
        # rece cmd_resp_data len
        rd_data = self.__axi4lite.read(0x22,2)
        resp_len = self.__data_deal.list_2_int(rd_data)
        # rece cmd_resp_data from resp_fifo
        aid_resp_data = []
        if(resp_len != 0):
            aid_resp_data = self.__axi4lite.read_array(0x80, resp_len, 8)
        if(vdg_poll_en_flag == 0x01):
            rd_data = self.__axi4lite.read(0x11,1)
            rd_data[0] = rd_data[0] | 0x10;
            self.__axi4lite.write(0x11, rd_data, 1)
        return aid_resp_data
    