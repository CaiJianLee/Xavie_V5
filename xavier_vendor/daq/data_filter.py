import socket
import struct
from ee.common import logger

def output(channel, frame_list):
    frame = frame_list[0]
    totalsent = 0
    datalen = len(frame)
    while totalsent < datalen:
        try:
            sent = channel._connector.send(frame)
        except socket.error, e:
            channel._poller.unregister(channel._connector.fileno())
            channel._connector.close()
            channel._connector = None
            return ("Error", e)
        except Exception, e:
            channel._connector = None
            return ("Error", e)
        else:
            if sent == 0:
                return ("Error", "socket connection broken")

            totalsent += sent

    return ("Done", None)
        
def divide_datalogger_channel(channel, frame_list): 
    try:
        frame = frame_list[0]
        frame_head = frame[:14]
        (payload_len,) = struct.unpack('<H',frame[14:16])
        old_payloads = frame[16:16+payload_len]

        new_payloads = ''
        for index in xrange(0, payload_len, 4):
            payload = old_payloads[index:index+4]
            (int_payload,) = struct.unpack('<i',payload)
            data_ch = int_payload & 0xf
           #logger.debug("int_payload=0x%X, %r" %(int_payload, payload))
            if data_ch == channel._channelid:
                new_payloads += payload
                #logger.debug("channelid=%r data_ch=%r"%(channel._channelid,data_ch))
        new_payload_len = len(new_payloads)
        new_frame = frame_head + struct.pack('>H',new_payload_len) + new_payloads + frame[16+payload_len:]
        #logger.debug("new_frame=%r"%(new_frame))
        frame_list[0] = new_frame
    except Exception as e:
        return ("Error", e)
    else:
        return ("Next", None)


