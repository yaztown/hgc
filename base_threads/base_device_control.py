'''
Created on Tuesday 03/07/2018

@author: yaztown
'''

from .base_threads import BaseThread

class BaseDeviceControl(BaseThread):
    '''
    BaseDeviceControl class is the base of all the device control classes such as
    the TimedDeviceControl class and sensor enabled device controls.
    '''
    
    def __init__(self, relay_pin=None, manual_control=False,
                 *args, **kwargs):
        '''
        Constructor
        '''
        super().__init__(*args, **kwargs)
        self.relay_pin = relay_pin
        self.manual_control = manual_control
        
        self._device_on = None     # Flag for Device power status
    
    def __work__(self):
        if not self.manual_control:
            self._auto_control()
    
    def _auto_control(self):
        '''
        All subclasses shall override this method
        e.g.: It can check the time or read a sensor threads value or ...
        '''
        raise NotImplementedError
    
    
    def set_manual(self):
        '''
        This method will set the operation of the device to manual as opposed to automatic
        (see set_auto() for the other type of operation)
        '''
        self.manual_control = True
    
    def set_automatic(self):
        '''
        This method will set the operation of the device to automatic as opposed to manual
        (see set_manual() for the other type of operation)
        '''
        self.manual_control = False
    
    
    def _on_(self):
        '''
        This is the method the does the actual turning on of the device
        by switching the relay pin to logic high.
        
        *** Note: If needed, subclasses should override this method not self.turn_on()
        '''
        raise NotImplementedError('TODO: must be implemented by assigning the correct logic on the relay_pin')
    
    def _off_(self):
        
        '''
        This is the method the does the actual turning off of the device
        by switching the relay pin to logic low.
        
        *** Note: If needed, subclasses should override this method not self.turn_off()
        '''
        raise NotImplementedError('TODO: must be implemented by assigning the correct logic on the relay_pin')
    
    # Device main On and Off methods
    def turn_on(self):
        '''
        This method is called to turn on the device.
        '''
        self._on_()
        self._device_on = True
    
    def turn_off(self):
        '''
        This method is called to turn off the device.
        '''
        self._off_()
        self._device_on = False
    
    @property
    def _serialized_(self):
        serialized = super()._serialized_
        serialized.update({
            'relayPin': self.relay_pin,
            'manualControl': self.manual_control,
            'deviceOn': self._device_on,
        })
        return serialized
