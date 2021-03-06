'''
Created on Tuesday 03/07/2018

@author: yaztown
'''
from datetime import datetime, timedelta, time
from base_threads import BaseController
from pin_out import MyGPIO
from hgc_logging import get_logger

logger = get_logger()

DEFAULT_CYCLES_PER_DAY = 1

class TimingController(BaseController):
    '''
    This class provides a timed (scheduled) control to operate the controller
    '''
    def __init__(self, time_on=None, duration_on=None, cycles_per_day=DEFAULT_CYCLES_PER_DAY,
                 *args, **kwargs):
        '''
        time_on        : is datetime.time() init parameters dictionary indicating the time to turn on the controller.
        duration_on    : is datetime.timedelta init parameters dictionary indicating the period of time until
                         turning the controller off again.
        cycles_per_day : is a factor indicating how many times per day to repeat the off/on/off cycle.
                         e.g.: A value of 2 will repeat twice a day (12 hours per cycle)
                               A value of 0.5 will repeat every other day (48 hours per cycle)
                               A value of 1 (default) will repeat everyday (24 hours per cycle)
        '''
        super().__init__(*args, **kwargs)
        
        if time_on is None or duration_on is None or cycles_per_day is None:
            raise ValueError('One or more parameters is None. Must specify time_on and duration')
        
        # TODO: Create a method for configuring the class's timing parameters outside the init method
        self.time_on = time(**time_on)
        self.cycles_per_day = cycles_per_day
        
        duration_on = timedelta(**duration_on)
        self.cycle_total_duration = timedelta(days=1)/cycles_per_day
        
        if duration_on >= self.cycle_total_duration:
            raise ValueError('Cannot manage (duration_on) with the provided (cycles_per_day)')
        
        self.duration_on = duration_on
        self.duration_off = self.cycle_total_duration - duration_on
        
        today = datetime.now().date()
        self.next_on = datetime.combine(today, self.time_on)
        self.next_off = self.next_on + self.duration_on
        self.setup_next_cycle()
    
    
    def config_controller(self, time_on, duration_on, cycles_per_day):
        self.time_on = time(**time_on)
        self.cycles_per_day = cycles_per_day
        
        duration_on = timedelta(**duration_on)
        self.cycle_total_duration = timedelta(days=1)/cycles_per_day
        
        if duration_on >= self.cycle_total_duration:
            raise ValueError('Cannot manage (duration_on) with the provided (cycles_per_day)')
        
        self.duration_on = duration_on
        self.duration_off = self.cycle_total_duration - duration_on
        
        today = datetime.now().date()
        self.next_on = datetime.combine(today, self.time_on)
        self.next_off = self.next_on + self.duration_on
        self.setup_next_cycle()

    
#     @classmethod
#     def from_time_on_and_time_off(cls, stime_on=None, stime_off=None, off_tomorrow=False, *args, **kwargs):
#         '''
#         stime_on : is a string object representing the Turn-On time with a 24-hour
#                   format "HH:MM:SS" e.g. "14:45:02", "15:56" or just "21".
#         stime_off: is a string object representing the Turn-Off time with a 24-hour
#                   format "HH:MM:SS" e.g. "15:55:15" and must be greater then time_on.
#         off_tomorrow: is a boolean indicating if the off time string happens the day after
#         '''
#         time_on = time( *map(int, stime_on.split(":")))
#         time_off = time( *map(int, stime_off.split(":")))
#         
#         if time_on >= time_off and not off_tomorrow:
#             raise ValueError('time_off must be greater than time_on')
#         
#         # The below varibles are datetime objects and are always moving
#         d_today = datetime.now().date()
#         d_tomorrow = d_today + timedelta(days=1)
#         
#         next_on = datetime.combine(d_today, time_on)
#         next_off = datetime.combine(d_tomorrow if off_tomorrow else d_today, time_off)
#         duration_on = next_off - next_on
#         
#         return cls(time_on=stime_on, duration_on=duration_on.seconds, *args, **kwargs)
    
    
    def setup_next_cycle(self):
        now = datetime.now()
        while now >= self.next_off:
            self.next_on = self.next_off + self.duration_off
            self.next_off = self.next_on + self.duration_on
    
    def _auto_control(self):
        now = datetime.now()
        
        if now < self.next_on:
            self.turn_off()
        elif now >= self.next_on and now < self.next_off:
            self.turn_on()
        else:
#             self.turn_off()
            self.setup_next_cycle()
    
    def _on_(self):
        if self._controller_on is not True:
            logger.debug('{} turned On.  Next Off @ {}'.format(self.name, self.next_off))
            MyGPIO().set_relay_on(self.relay_pin)
    
    def _off_(self):
        if self._controller_on is not False:
            logger.debug('{} turned Off.  Next On @ {}'.format(self.name, self.next_on))
            MyGPIO().set_relay_off(self.relay_pin)

    @property
    def _serialized_(self):
        serialized = super()._serialized_
        serialized.update({'info': {
            'time_on': self.time_on,
            'duration_on': self.duration_on,
            'cycles_per_day': self.cycles_per_day,
            'cycle_total_duration': self.cycle_total_duration,
            'next_on': self.next_on,
            'next_off': self.next_off,
        }})
        return serialized
