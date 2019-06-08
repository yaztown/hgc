'''
Created on Monday 11/03/2019

@author: yaztown
'''
from base_threads import BaseThread
from .myjson import MyJSONEncoder


class HGCJSONEncoder(MyJSONEncoder):
    '''
    This JSONEncoder subclass add datetime.{datetime,date,time} objects
    to the default encoded types 
    '''
    def default(self, obj):
        if BaseThread in obj.__class__.mro():
#         if isinstance(obj, HumidityTemperatureSensor) \
#             or isinstance(obj, DeviceHumidityCompareControl) \
#             or isinstance(obj, DeviceTempCompareControl) \
#             or isinstance(obj, DeviceTimingControl):
            return {
                '_type': obj.__class__.__name__,
                'value': obj._serialized_
            }
        return super().default(obj)
