'''
Created on Monday 11/03/2019

@author: yaztown
'''

import json, urllib, re

from .urls import urls_conf

error_message = 'Big fat Error message.'

class SimpleURLHandler(object):
    '''
    classdocs
    '''
    
    def __init__(self, request):
        '''
        Constructor
        '''
        self.request = request
    
    def handle(self):
        for url_conf in urls_conf:
            p = re.compile(url_conf[0])
            m = None
            m = p.match(self.request['path'])
            del p
            if m is not None:
                params = m.groupdict()
                return url_conf[1](params)
        return error_message
