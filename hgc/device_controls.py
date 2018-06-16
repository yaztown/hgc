'''
Created on Tuesday 12/06/2018

@author: yaztown
'''
from time import sleep
from datetime import time, datetime, timedelta
import threading

import logging

logging.basicConfig(
#     level=logging.DEBUG,
    level=logging.NOTSET,
    format='[%(asctime)s] (%(threadName)-15s) %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)


DEFAULT_SLEEP_TIME = 10
DEFAULT_CYCLES_PER_DAY = 1

class DeviceControl(threading.Thread):
    '''
    This class controls the device's On/Off timing
    '''

    def __init__(self, name, time_on, duration_on, sleep_time=DEFAULT_SLEEP_TIME, cycles_per_day=DEFAULT_CYCLES_PER_DAY):
        '''
        name: is a general name for the DeviceControl thread.
        time_on: is a datetime.time() object indicating the time to turn on the device.
        duration_on: is a datetime.timedelta object indicating the period of time until
                     turning the device off again.
        '''
        super().__init__()
        self.sleep_time = sleep_time
        
        self.name = name
        self.time_on = time_on
        self._exit_loop = False
        
        cycle_total_duration = timedelta(days=1)/cycles_per_day
        self.duration_on = duration_on
        self.duration_off = cycle_total_duration - duration_on
        
        today = datetime.now().date()
        self.next_on = datetime.combine(today, time_on)
        self.next_off = self.next_on + self.duration_on
    
    
    @classmethod
#     def fromTimeOnTimeOff(cls, ton_h, ton_m, ton_s, toff_h, toff_m, toff_s):
    def fromTimeOnTimeOff(cls, name, stime_on, stime_off, off_tomorrow=False, sleep_time=DEFAULT_SLEEP_TIME, cycles_per_day=DEFAULT_CYCLES_PER_DAY):
        '''
        stime_on : is a string object representing the Turn-On time with a 24-hour
                  format "HH:MM:SS" e.g. "14:45:02", "15:56" or just "21".
        stime_off: is a string object representing the Turn-Off time with a 24-hour
                  format "HH:MM:SS" e.g. "15:55:15" and must be greater then time_on.
        off_tomorrow: is a boolean indicating if the off time string happens the day after
        '''
        time_on = time( *map(int, stime_on.split(":")))
        time_off = time( *map(int, stime_off.split(":")))
        
        if time_on >= time_off and not off_tomorrow:
            raise ValueError('time_off must be greater than time_on')
        
        # The below varibles are datetime objects and are always moving
        d_today = datetime.now().date()
        d_tomorrow = d_today + timedelta(days=1)
        
        next_on = datetime.combine(d_today, time_on)
        next_off = datetime.combine(d_tomorrow if off_tomorrow else d_today, time_off)
        duration_on = next_off - next_on
        
        return cls(name=name, time_on=time_on, duration_on=duration_on, sleep_time=sleep_time, cycles_per_day=cycles_per_day)
    
    
    def setupNextCycle(self):
        self.next_on = self.next_off + self.duration_off
        self.next_off = self.next_on + self.duration_on
    
    def stop(self):
        self._exit_loop = True
    
    def run(self):
        while not self._exit_loop:
            now = datetime.now()
            
            if now < self.next_on:
                logging.debug('Device Off')
            elif now >= self.next_on and now < self.next_off:
                logging.debug('Device On')
            else:
                logging.debug('Device Off')
                self.setupNextCycle()
            
            sleep(10)


if __name__ == '__main__':
    t_on = time(16,55)
    th = DeviceControl('veg', t_on, 2)
    th.start()
    while True:
        print('main thread')
        sleep(30)


