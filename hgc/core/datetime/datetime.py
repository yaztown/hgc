'''
Created on Wednesday 12/06/2019

@author: yaztown
'''

TIME_ZONE = 'Asia/Riyadh'

from datetime import datetime
import pytz

HGC_TZINFO = pytz.timezone(TIME_ZONE)

def tzAwareDate(date, tzinfo=HGC_TZINFO):
    return date.replace(tzinfo=tzinfo)

def tzNow():
    return datetime.now(tz=HGC_TZINFO)

class TzAwareDatetime(datetime):
    def __new__(self, *args, **kwargs):
        kwargs['tzinfo'] = pytz.timezone(TIME_ZONE)
        return datetime.__new__(self, *args, **kwargs)
    
    @classmethod
    def now(cls, *args, **kwargs):
        kwargs['tz'] = pytz.timezone(TIME_ZONE)
        return cls.now(**kwargs)
