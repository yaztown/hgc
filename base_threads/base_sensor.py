'''
Created on Tuesday 03/07/2018

@author: yaztown
'''

from .base_threads import BaseThread

class BaseSensor(BaseThread):
    '''
    BaseDevice class is the base of all the device control classes such as
    the TimedDeviceControl class and sensor enabled device controls.
    
    Subclasses must inherit self._read_sensor() since it is part of the thread run process
    The other method to inherit is self.get_reading() which is used by the other device control
    classes in this module.
    '''
    
    def __init__(self, sensor=None, *args, **kwargs):
        '''
        Constructor
        '''
        super().__init__(*args, **kwargs)
        self.sensor = sensor
    
    def __work__(self):
        self._read_sensor()
    
    def _read_sensor(self):
        raise NotImplementedError
    
    def get_reading(self):
        raise NotImplementedError
