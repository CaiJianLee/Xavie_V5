__author__ = 'Mingcheng'

import zmq 
import datetime
import threading

class Publisher(object):
    
    def __init__(self, identity):
        print 'Publish init: ' + identity
        self.identity = identity
        
    def publish(self, msg, id_postfix=None, level = 'DEBUG'):
        t= datetime.datetime.now()
        ts = datetime.datetime.strftime(t, '%m-%d_%H:%M:%S.%f')
        id_str = self.identity
        if id_postfix:
            id_str = id_str + '--' + id_postfix
            
        self._send(ts, id_str, msg, level)
 
class ZmqPublisher(Publisher):
     
    def __init__(self, ctx, endpoint, identity):
        print 'ZmqPublish init'
        super(ZmqPublisher, self).__init__(identity)
        self.publisher = ctx.socket(zmq.PUB)
        self.publisher.setsockopt(zmq.IDENTITY, identity)
        self.publisher.bind(endpoint)
        self.lock = threading.Lock()
        print 'ZmqPublish init finish'
        
    def _send(self, ts, id_str, msg, level):
        #zmq socket is not thread safe
        self.lock.acquire()
        self.publisher.send_multipart([str(186), str(ts), str(level), str(id_str), str(msg)])
        self.lock.release()

    def __del__(self):
        if not self.publiser.closed:
            if zmq is None: #the zmq module may have been released by this time
                return
            
            self.publisher.setsockopt(zmq.LINGER, 0)
            self.publisher.close()
