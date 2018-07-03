'''
Created on Monday 03/07/2018
@author: yaztown
humidity_temperature_sensor
HT_SENSORS is the supported sensor dictionary

'''

from . import Adafruit_DHT
#import Adafruit_DHT
from collections import deque
from base_threads import BaseSensor
from datetime import datetime
from os import path
import threading


HT_SENSORS = {
        '11': Adafruit_DHT.DHT11,
        '22': Adafruit_DHT.DHT22,
        '2302': Adafruit_DHT.AM2302
    }

class HumidityTemperatureSensor(BaseSensor):
    '''
    HumidityTemperatureSensor thread class
    '''
    def __init__(self, data_pin=None, sensor='22', buff_maxlen=5,
                 save_data=False, save_data_dir='',
                 max_accepted_humidity=100, min_accepted_humidity=0,
                 max_accepted_temperature=100, min_accepted_temperature=0,
                 *args, **kwargs):
        '''
        data_pin                 :
        sensor                   :
        buff_maxlen              :
        save_data                :
        save_data_dir            :
        max_accepted_humidity    :
        min_accepted_humidity    :
        max_accepted_temperature :
        min_accepted_temperature :
        '''
        super().__init__(*args, **kwargs)
        self.data_pin = data_pin
        self.sensor = HT_SENSORS[sensor]
        self.buff_maxlen = buff_maxlen
        self.dq_humidity = deque(maxlen=self.buff_maxlen)
        self.dq_temperature = deque(maxlen=self.buff_maxlen)
        self.save_data = save_data
        self.save_data_dir = save_data_dir
        self.max_accepted_humidity = max_accepted_humidity
        self.min_accepted_humidity = min_accepted_humidity
        self.max_accepted_temperature = max_accepted_temperature
        self.min_accepted_temperature = min_accepted_temperature
    
    def write_data_to_file(self, humidity, temperature):
        l = threading.Lock()
        file_name = 'weather_data_{:%Y_%m_%d}.txt'.format(datetime.now())
        file_path = path.join(self.save_data_dir, file_name)
        l.acquire()
        with open(file_path, 'a+') as fd:
            fd.write('{0:%H%M%S}\t{1:.1f}\t{2:.1f}\n'.format(datetime.now(), humidity, temperature))
        l.release()
 
        #TODO: Fix the commented area
    def is_reading_accepted(self, h, t):
        hh = tt = False
        if h is not None and t is not None:
            if h >= self.min_accepted_humidity and h <= self.max_accepted_humidity:
                hh = True
            if t >= self.min_accepted_temperature and t <= self.max_accepted_temperature:
                tt = True
        return hh and tt

    def _read_sensor(self):
        h, t = Adafruit_DHT.read_retry(self.sensor, self.data_pin)
        if h is not None and t is not None and self.is_reading_accepted(h, t):
            self.dq_humidity.append(h)
            self.dq_temperature.append(t)
            if self.save_data:
                self.write_data_to_file(h, t)
    
    # the sensor's data
    
    def get_last_reading_humidity(self):
        l = threading.Lock()
        l.acquire()
        i = len(self.dq_humidity)
        ret = self.dq_humidity[i-1]
        l.release()
        return ret
    
    def get_last_reading_temperature(self):
        l = threading.Lock()
        l.acquire()
        i = len(self.dq_temperature)
        ret = self.dq_temperature[i-1]
        l.release()
        return ret
    
    def get_last_reading(self):
        return dict(humidity=self.get_last_reading_humidity(), temperature=self.get_last_reading_temperature())
    
    
# TODO: Add a minute average readings
    def get_avg_minute_reading_humidity(self):
        return None
    
# TODO: Add a minute average readings
    def get_avg_minute_reading_temperature(self):
        return None
    
    def get_avg_minute_reading(self):
        return dict(humidity=self.get_avg_minute_reading_humidity(), temperature=self.get_avg_minute_reading_temperature())
    
    
    def get_avg_moving_reading_humidity(self):
        l = threading.Lock()
        l.acquire()
        sm = sum(self.dq_humidity)
        sl = len(self.dq_humidity)
        l.release()
        return sm/sl

    def get_avg_moving_reading_temperature(self):
        l = threading.Lock()
        l.acquire()
        sm = sum(self.dq_temperature)
        sl = len(self.dq_temperature)
        l.release()
        return sm/sl
    
    def get_avg_moving_reading(self):
        return dict(humidity=self.get_avg_moving_reading_humidity(), temperature=self.get_avg_moving_reading_temperature())
