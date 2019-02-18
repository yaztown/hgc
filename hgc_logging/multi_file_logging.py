'''
Created on Monday 11/02/2019

@author: yaztown
'''

from datetime import date

import logging
import os

class DatedMultiFileHandler(logging.Handler):
    '''
    A handler class which writes logging records, appropriately formatted,
    to multiple files with names based of the date and thread name. Note that this class does not close the stream, as
    sys.stdout or sys.stderr may be used.

    '''
    
    terminator = '\n'
    
    def __init__(self, log_path, mode='a', encoding=None, create_subfolders=False, level=logging.NOTSET):
        '''
        Constructor
        '''
        super().__init__(level)
        if not os.access(log_path, os.W_OK):
            raise Exception("Path: {} not writeable".format(log_path))
        self.log_path = log_path
        self._files = {}
        self.mode = mode
        self.encoding = encoding
        self.create_subfolders = create_subfolders
        self._today = date.today()
    
    def _get_date_prefix(self):
        return date.today().isoformat()
    
    def files_cleanup(self):
        '''
        Closes all streams.
        '''
        self.acquire()
        self._today = date.today()
        try:
            try:
                for log_file in self._files.values():
                    log_file.close()
            finally:
                # Issue #19523: call unconditionally to
                # prevent a handler leak when delay is set
                super().close()
        finally:
            self.release()
    
    def close(self):
        self.files_cleanup()
    
    def _get_or_open(self, key):
        '''
        Get the file pointer for the given key, or else open the file
        '''
        self.acquire()
        
        file_name = '{}__{}'.format(self._get_date_prefix(), key)
        
        try:
            if not self._files.has_key(file_name):
                self._files[file_name] = open(os.path.join(self.log_path, file_name + '.log'), 'a')
            return self._files[file_name]
        finally:
            self.release()
    
    def emit(self, record):
        # No lock here; following code for StreamHandler and FileHandler
        try:
            if self._today != date.today():
                self.files_cleanup()
            fp = self._get_or_open(record.threadName)
            msg = self.format(record)
            fp.write(msg)
            fp.write(self.terminator)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
