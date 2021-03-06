'''
Created on Monday 13/05/2019

@author: yaztown
'''

from hgc.core.metaclasses import Singleton
from RPi import GPIO

GPIO.setwarnings(False)

class MyGPIO(metaclass=Singleton):
    OUT = GPIO.OUT
    IN = GPIO.IN
    HIGH = GPIO.HIGH
    LOW = GPIO.LOW
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.initialized = True
    
    def setup(self, channel=None, direction=None, **kwargs):
        if (channel is None) or (direction is None):
            return
        GPIO.setup(channel, direction, **kwargs)
    
    def read(self, channel=None):
        if channel is None:
            return
        return GPIO.input(channel)
    
    def output(self, channel=None, value=None):
        if (channel is None) or (value is None):
            return
        return GPIO.output(channel, value)
    
    def set_relay_on(self, channel):
        GPIO.output(channel, GPIO.LOW)
    
    def set_relay_off(self, channel):
        GPIO.output(channel, GPIO.HIGH)
