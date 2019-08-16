'''
Created on Tuesday 03/07/2018

@author: yaztown
'''

from .base_threads import BaseThread

from pin_out import MyGPIO

class BaseController(BaseThread):
    '''
    BaseController class is the base of all controller classes such as
    the TimedController class and sensor powered controllers.
    '''
    
    def __init__(self, relay_pin=None, manual_control=False,
                 *args, **kwargs):
        '''
        Constructor
        '''
        super().__init__(*args, **kwargs)
        self.relay_pin = relay_pin
        if not relay_pin is None:
            gpio = MyGPIO()
            gpio.setup(self.relay_pin, gpio.OUT)
        self.manual_control = manual_control
        
        self._controller_on = None     # Flag for controller power status
    
    def config_controller(self, **kwargs):
        raise NotImplementedError
    
    def __loop__(self):
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
        This method will set the operation of the controller to manual as opposed to automatic
        (see set_auto() for the other type of operation)
        '''
        self.manual_control = True
    
    def set_automatic(self):
        '''
        This method will set the operation of the controller to automatic as opposed to manual
        (see set_manual() for the other type of operation)
        '''
        self.manual_control = False
    
    
    def _on_(self):
        '''
        This is the method that does the actual turning on of the controller
        by switching the relay pin to logic high.
        
        *** Note: If needed, subclasses should override this method not self.turn_on()
        '''
        raise NotImplementedError('TODO: must be implemented by assigning the correct logic on the relay_pin')
    
    def _off_(self):
        
        '''
        This is the method the does the actual turning off of the controller
        by switching the relay pin to logic low.
        
        *** Note: If needed, subclasses should override this method not self.turn_off()
        '''
        raise NotImplementedError('TODO: must be implemented by assigning the correct logic on the relay_pin')
    
    # Controller main On and Off methods
    def turn_on(self):
        '''
        This method is called to turn on the controller.
        '''
        self._on_()
        self._controller_on = True
    
    def turn_off(self):
        '''
        This method is called to turn off the controller.
        '''
        self._off_()
        self._controller_on = False
    
    def manual_turn_on(self):
        self.set_manual()
        self.turn_on()
    
    def manual_turn_off(self):
        self.set_manual()
        self.turn_off()
    
    @property
    def _serialized_(self):
        serialized = super()._serialized_
        serialized.update({
            'relay_pin': self.relay_pin,
            'manual_control': self.manual_control,
            '_controller_on': self._controller_on,
        })
        return serialized
