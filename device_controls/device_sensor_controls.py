'''
Created on Tuesday 03/07/2018

@author: yaztown
'''

from base_threads import BaseDeviceControl
# from sensors import HumidityTemperatureSensor

import weakref


class DeviceHumTempSensorControl(BaseDeviceControl):
    '''
    This class controls the device's On/Off using a sensor
    '''
    def __init__(self, sensor=None,
                 threshold_humidity_upper=100, threshold_humidity_lower=0,
                 threshold_temp_upper=100, threshold_temp_lower=0,
                 *args, **kwargs):
        '''
        sensor_list             : is a list of sensor threads
        threshold_humidity_upper: is the humidity limit that will turn on the device 
        threshold_humidity_lower: is the humidity limit that will turn off the device
        threshold_temp_upper    : is the temperature limit that will turn on the device
        threshold_temp_lower    : is the temperature limit that will turn off the device
        '''
        super().__init__(*args, **kwargs)
        
        if sensor is None:
            raise ValueError('Must provide a sensor object.')
        self._sensor_ref = weakref.ref(sensor)
        
        self.threshold_hum_upper = threshold_humidity_upper
        self.threshold_hum_lower = threshold_humidity_lower
        self.threshold_temp_upper = threshold_temp_upper
        self.threshold_temp_lower = threshold_temp_lower
    
    def read_sensor(self):
        reading = self._sensor_ref().get_reading()
        return reading['humidity'], reading['temperature']
    
    def check_thresholds(self):
        hum, temp = self.read_sensor()
        
        if not self._device_on:
            if hum >= self.thr_hum_upper or temp >= self.thr_temp_upper:
                return True
            else:
                return False
        else:
            if hum >= self.thr_hum_lower or temp >= self.thr_temp_lower:
                return True
            else:
                return False
    
    def _auto_control(self):
        if self.check_thresholds():
            self.turn_on()
        else:
            self.turn_off()
    
    def _on_(self):
        raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')
    
    def _off_(self):
        raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')
