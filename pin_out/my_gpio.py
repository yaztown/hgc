'''
Created on Monday 13/05/2019

@author: yaztown
'''


from RPi import GPIO

class Singleton(type):
    '''
    classdocs
    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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
    
    def setRelayOn(self, channel):
        GPIO.output(channel, GPIO.LOW)
    
    def setRelayOff(self, channel):
        GPIO.output(channel, GPIO.HIGH)
    
