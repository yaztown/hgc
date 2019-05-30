'''
Created on Tuesday 03/07/2018

@author: yaztown
'''

import weakref

from base_threads import BaseDeviceControl
from sensors import HumidityTemperatureSensor
from pin_out import MyGPIO
from hgc_logging import get_logger

logger = get_logger()

class DeviceHumTempSensorControl(BaseDeviceControl):
    '''
    This class controls the device's On/Off using a sensor
    '''
    def __init__(self, sensor_name=None,
                 threshold_humidity_upper=100,
                 threshold_humidity_lower=0,
                 threshold_temp_upper=100,
                 threshold_temp_lower=0,
                 *args, **kwargs):
        '''
        sensor_name             : is name of the sensor threads
        threshold_humidity_upper: is the humidity limit that will turn on the device 
        threshold_humidity_lower: is the humidity limit that will turn off the device
        threshold_temp_upper    : is the temperature limit that will turn on the device
        threshold_temp_lower    : is the temperature limit that will turn off the device
        '''
        super().__init__(*args, **kwargs)
        _sensor = HumidityTemperatureSensor.get_sensor(sensor_name)
        if _sensor is None:
            raise ValueError('Sensor not found')
        self._sensor_ref = weakref.ref(_sensor)
        
        self.threshold_hum_upper = threshold_humidity_upper
        self.threshold_hum_lower = threshold_humidity_lower
        self.threshold_temp_upper = threshold_temp_upper
        self.threshold_temp_lower = threshold_temp_lower
    
    def read_sensor(self):
        reading = self._sensor_ref().get_reading()
        return reading['humidity'], reading['temperature']
    
    def check_thresholds(self):
        hum, temp = self.read_sensor()
        
        if hum is None or temp is None:
            return self._device_on
        
        if self._device_on:
            if hum >= self.threshold_hum_lower or temp >= self.threshold_temp_lower:
                return True
            else:
                return False
        else:
            if hum >= self.threshold_hum_upper or temp >= self.threshold_temp_upper:
                return True
            else:
                return False
        
    def _auto_control(self):
        if self.check_thresholds():
            self.turn_on()
        else:
            self.turn_off()
    
    def _on_(self):
        if self._device_on is not True:
            logger.debug('Turned On at Humidity: {humidity}\tTemperature: {temperature}'.format(**self._sensor_ref().get_reading()))
#         raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')
    
    def _off_(self):
        if self._device_on is not False:
            logger.debug('Turned Off at Humidity: {humidity}\tTemperature: {temperature}'.format(**self._sensor_ref().get_reading()))
#         raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')



class DeviceSensorsCompareControl(BaseDeviceControl):
    '''
    This class controls the device's On/Off using two sensors; one inside the box and the other outside.
    The controller will compare the inside temp to the maximum threshold and the lower being the outside temp.
    '''
    def __init__(self, sensor_in_name=None, sensor_out_name=None,
                 threshold_temp_upper=28,
                 *args, **kwargs):
        '''
        sensor_in_name          : is name of the inside sensor thread
        sensor_out_name         : is name of the outside sensor thread
        threshold_temp_upper    : is the temperature limit that will turn on the device
        '''
        super().__init__(*args, **kwargs)
        _sensor_in = HumidityTemperatureSensor.get_sensor(sensor_in_name)
        _sensor_out = HumidityTemperatureSensor.get_sensor(sensor_out_name)
        if _sensor_in is None or _sensor_out is None:
            raise ValueError('Sensor not found')
        self._sensor_in_ref = weakref.ref(_sensor_in)
        self._sensor_out_ref = weakref.ref(_sensor_out)
        
        self.threshold_temp_upper = threshold_temp_upper
    
    def read_sensors(self):
        reading_in = self._sensor_in_ref().get_reading()
        reading_out = self._sensor_out_ref().get_reading()
        return reading_in, reading_out
    
    def check_thresholds(self):
        tolerance = 1.04
        reading_in, reading_out = self.read_sensors()
        
        temp_in = reading_in['temperature']
        temp_out = reading_out['temperature']
        
        if temp_in is None or temp_out is None:
            return self._device_on
        
        if self._device_on:
            if temp_in >= (temp_out * tolerance):
                return True
            else:
                return False
        else:
            if temp_in >= self.threshold_temp_upper:
                return True
            else:
                return False
        
    def _auto_control(self):
        if self.check_thresholds():
            self.turn_on()
        else:
            self.turn_off()
    
    def _on_(self):
        if self._device_on is not True:
            logger.debug('Turned On at Humidity: {humidity:.1f}\tTemperature: {temperature:.1f}'.format(**self._sensor_in_ref().get_reading()))
            #raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')
    
    def _off_(self):
        if self._device_on is not False:
            logger.debug('Turned Off at Humidity: {humidity:.1f}\tTemperature: {temperature:.1f}'.format(**self._sensor_in_ref().get_reading()))
            #raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')


class DeviceHumidityCompareControl(BaseDeviceControl):
    '''
    This class controls the device's On/Off using two sensors; one inside the box and the other outside.
    The controller will compare the inside humidity to the maximum threshold and the lower being the outside temp.
    '''
    def __init__(self, sensor_in_name=None, sensor_out_name=None,
                 threshold_humidity_upper=70, tolerance=1.04,
                 *args, **kwargs):
        '''
        sensor_in_name           : is name of the inside sensor thread
        sensor_out_name          : is name of the outside sensor thread
        threshold_humidity_upper : is the humidity limit that will turn on the device
        '''
        super().__init__(*args, **kwargs)
        _sensor_in = HumidityTemperatureSensor.get_sensor(sensor_in_name)
        _sensor_out = HumidityTemperatureSensor.get_sensor(sensor_out_name)
        if _sensor_in is None or _sensor_out is None:
            raise ValueError('Sensor not found')
        self._sensor_in_ref = weakref.ref(_sensor_in)
        self._sensor_out_ref = weakref.ref(_sensor_out)
        self.tolerance = tolerance
        self.threshold_humidity_upper = threshold_humidity_upper
    
    def read_sensors(self):
        reading_in = self._sensor_in_ref().get_reading()
        reading_out = self._sensor_out_ref().get_reading()
        return reading_in, reading_out
    
    def check_thresholds(self):
        reading_in, reading_out = self.read_sensors()
        
        humidity_in = reading_in['humidity']
        humidity_out = reading_out['humidity']
        
        if humidity_in is None or humidity_out is None:
            return self._device_on
        
        if self._device_on:
            if humidity_in >= (humidity_out * self.tolerance):
                return True
            else:
                return False
        else:
            if humidity_in >= self.threshold_humidity_upper:
                return True
            else:
                return False
        
    def _auto_control(self):
        if self.check_thresholds():
            self.turn_on()
        else:
            self.turn_off()
    
    def _on_(self):
        if self._device_on is not True:
            logger.debug('Turned On at Humidity: {humidity:.1f}\tTemperature: {temperature:.1f}'.format(**self._sensor_in_ref().get_reading()))
            #raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')
    
    def _off_(self):
        if self._device_on is not False:
            logger.debug('Turned Off at Humidity: {humidity:.1f}\tTemperature: {temperature:.1f}'.format(**self._sensor_in_ref().get_reading()))
            #raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')

    @property
    def _serialized_(self):
        serialized = super()._serialized_
        serialized.update({'info': {
            '_sensor_in_name': self._sensor_in_ref().name,
            '_sensor_out_name': self._sensor_out_ref().name,
            'threshold_humidity_upper': self.threshold_humidity_upper,
            'tolerance': self.tolerance,
        }})
        return serialized



class DeviceTempCompareControl(BaseDeviceControl):
    '''
    This class controls the device's On/Off using two sensors; one inside the box and the other outside.
    The controller will compare the inside temp to the maximum threshold and the lower being the outside temp.
    '''
    def __init__(self, sensor_in_name=None, sensor_out_name=None,
                 threshold_temp_upper=28, tolerance=1.04,
                 *args, **kwargs):
        '''
        sensor_in_name          : is name of the inside sensor thread
        sensor_out_name         : is name of the outside sensor thread
        threshold_temp_upper    : is the temperature limit that will turn on the device
        '''
        super().__init__(*args, **kwargs)
        _sensor_in = HumidityTemperatureSensor.get_sensor(sensor_in_name)
        _sensor_out = HumidityTemperatureSensor.get_sensor(sensor_out_name)
        if _sensor_in is None or _sensor_out is None:
            raise ValueError('Sensor not found')
        self._sensor_in_ref = weakref.ref(_sensor_in)
        self._sensor_out_ref = weakref.ref(_sensor_out)
        self.tolerance = tolerance
        self.threshold_temp_upper = threshold_temp_upper
    
    def read_sensors(self):
        reading_in = self._sensor_in_ref().get_reading()
        reading_out = self._sensor_out_ref().get_reading()
        return reading_in, reading_out
    
    def check_thresholds(self):
        reading_in, reading_out = self.read_sensors()
        
        temp_in = reading_in['temperature']
        temp_out = reading_out['temperature']
        
        if temp_in is None or temp_out is None:
            return self._device_on
        
        if self._device_on:
            if temp_in >= (temp_out * self.tolerance):
                return True
            else:
                return False
        else:
            if temp_in >= self.threshold_temp_upper:
                return True
            else:
                return False
        
    def _auto_control(self):
        if self.check_thresholds():
            self.turn_on()
        else:
            self.turn_off()
    
    def _on_(self):
        if self._device_on is not True:
            logger.debug('Turned On at Humidity: {humidity:.1f}\tTemperature: {temperature:.1f}'.format(**self._sensor_in_ref().get_reading()))
            #raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')
    
    def _off_(self):
        if self._device_on is not False:
            logger.debug('Turned Off at Humidity: {humidity:.1f}\tTemperature: {temperature:.1f}'.format(**self._sensor_in_ref().get_reading()))
            #raise NotImplementedError('Should import the RPi.GPIO and do output the pin with the correct logic.')
    
    @property
    def _serialized_(self):
        serialized = super()._serialized_
        serialized.update({'info': {
            '_sensor_in_ref': self._sensor_in_ref().name,
            '_sensor_out_ref': self._sensor_out_ref().name,
            'threshold_temp_upper': self.threshold_temp_upper,
            'tolerance': self.tolerance,
        }})
        return serialized


from time import time

class SensorTimeLimitController(BaseDeviceControl):
    '''
    This class controls the device's On/Off using a sensor and a timed operation.
    The controller will compare the reading to the upper threshold and the lower being the outside temp.
    '''
    def __init__(self, sensor_name=None,
                 threshold_upper=28,
                 threshold_lower=20,
                 max_duration_on=300,
                 min_duration_off=300,
                 reading_type='temperature',
                 *args, **kwargs):
        '''
        sensor_name             : is name of the sensor thread
        threshold_temp_upper    : is the temperature limit that will turn on the device
        threshold_temp_lower    : is the temperature limit that will turn off the device
        max_duration_on         : is the maximum duration, in seconds, for the device to be on
        min_duration_off        : is the minimum duration, in seconds, for the device to be off
        reading_type            : 'temperature', 'humidity', 'light', 'moisture', 'co2'

        '''
        super().__init__(*args, **kwargs)
        
        _sensor = HumidityTemperatureSensor.get_sensor(sensor_name)
        if _sensor is None:
            raise ValueError('Sensor not found')
        
        self._sensor_ref = weakref.ref(_sensor)
        self.threshold_upper = threshold_upper
        self.threshold_lower = threshold_lower
        self.max_duration_on = max_duration_on,
        self.min_duration_off = min_duration_off
        self.reading_type = reading_type
        
        # setup member variables
        self.turn_off_time = time()
        self.turn_on_time = None
        self.on_cycle = False
        
    
    def read_sensors(self):
        return self._sensor_ref().get_reading()
    
    def check_upper_threshold(self):
        reading = self.read_sensors()
        sensor_value = reading[self.reading_type]
        return (sensor_value >= self.threshold_upper)
    
    def check_lower_threshold(self):
        reading = self.read_sensors()
        sensor_value = reading[self.reading_type]
        return (sensor_value <= self.threshold_lower)
    
    def _auto_control(self):
        if self.on_cycle:
            if self.check_lower_threshold() or ((time() - self.turn_on_time) >= self.max_duration_on):
                self.turn_off()
                self.turn_off_time = time()
                self.on_cycle = False
                self.turn_on_time = None
        elif self.check_upper_threshold() and ((time() - self.turn_off_time) > self.min_duration_off):
            self.turn_on()
            self.turn_on_time = time()
            self.on_cycle = True
            self.turn_off_time = None
#         else:
#             self.turn_off()
#             self.turn_off_time = time()
#             self.on_cycle = False
#             self.turn_on_time = None
    
    def _on_(self):
        if self._device_on is not True:
            sensor_value = self._sensor_ref().get_reading()[self.reading_type]
            logger.debug('Turned On at {}: {:.1f}'.format(self.reading_type, sensor_value))
            MyGPIO().set_relay_on(self.relay_pin)

    
    def _off_(self):
        if self._device_on is not False:
            sensor_value = self._sensor_ref().get_reading()[self.reading_type]
            logger.debug('Turned Off at {}: {:.1f}'.format(self.reading_type, sensor_value))
            MyGPIO().set_relay_off(self.relay_pin)
    
    @property
    def _serialized_(self):
        serialized = super()._serialized_
        serialized.update({'info': {
            '_sensor': self._sensor_in_ref().name,
            'threshold_upper': self.threshold_upper,
            'threshold_lower': self.threshold_lower,
            'max_duration_on': self.max_duration_on,
            'min_duration_off': self.min_duration_off,
            'reading_type': self.reading_type,
        }})
        return serialized

