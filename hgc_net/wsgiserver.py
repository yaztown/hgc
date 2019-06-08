'''
Created on Thursday 06/06/2019

@author: yaztown
'''
import threading
import wsgiserver
from hgc_logging import get_logger as getLogger

logger = getLogger()

class WSThread(threading.Thread):
    def __init__(self, wsgi_app, host='0.0.0.0', port=8000, numthreads=10,
                 server_name='hgc_server', threadpool_max=-1, request_queue_size=5, timeout=10,
                 shutdown_timeout=5, accepted_queue_size=-1,
                 accepted_queue_timeout=10, certfile=None, keyfile=None,
                 ca_certs=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        if wsgi_app is None:
            raise ValueError('wsgi_app must be defined.')
        self.app = wsgi_app
        self.server = wsgiserver.WSGIServer(
            self.app, host=host, port=port, numthreads=numthreads,
            server_name=server_name, max=threadpool_max, request_queue_size=request_queue_size,timeout=timeout,
            shutdown_timeout=shutdown_timeout, accepted_queue_size=accepted_queue_size,
            accepted_queue_timeout=accepted_queue_timeout,
            certfile=certfile, keyfile=keyfile, ca_certs=ca_certs,
            )
        logger.debug('Initialized wsgiserver')
    
    def run(self):
        logger.debug('Starting wsgiserver @ http://{}:{}/'.format(*self.server.bind_addr))
        self.server.start()
        logger.debug('Stopped wsgiserver')
        
    
    def stop(self):
        logger.debug('Stopping wsgiserver')
        self.server.stop()
