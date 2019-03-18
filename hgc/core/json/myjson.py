'''
Created on Monday 18/03/2019

@author: yaztown
'''
import json
# import re
import datetime

FORMAT_DATE = '%Y-%m-%d'
FORMAT_TIME = '%H:%M:%S'
FORMAT_DATETIME = '{}T{}'.format(FORMAT_DATE, FORMAT_TIME)

class MyJSONEncoder(json.JSONEncoder):
    '''
    This JSONEncoder subclass add datetime.{datetime,date,time} objects
    to the default encoded types 
    '''
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                '_type': 'datetime', #obj.__class__.__name__,
#                 'value': obj.strftime(FORMAT_DATETIME)
                'value': obj.isoformat()
            }
        elif isinstance(obj, datetime.date):
            return {
                '_type': 'date', #obj.__class__.__name__,
                'value': obj.strftime(FORMAT_DATE)
            }
        elif isinstance(obj, datetime.time):
            return {
                '_type': 'time', #obj.__class__.__name__,
                'value': obj.strftime(FORMAT_TIME)
            }
        elif isinstance(obj, datetime.timedelta):
            _days = obj.days
            _seconds = obj.seconds
            _minutes = _seconds // 60
            _seconds = _seconds % 60
            _hours = _minutes // 60
            _minutes = _minutes % 60
            return {
                '_type': 'timedelta', #obj.__class__.__name__,
                'value': {
                    'days': _days,
                    'hours': _hours,
                    'minutes': _minutes,
                    'seconds': _seconds
                }
            }
        return super().default(obj)


def _parse_datetime(sdatetime):
    return datetime.datetime.strptime(sdatetime, FORMAT_DATETIME)

def _parse_date(sdate):
    return datetime.datetime.strptime(sdate, FORMAT_DATE).date()

def _parse_time(stime):
    return datetime.datetime.strptime(stime, FORMAT_TIME).time()

def _parse_timedelta(td_dict):
    _days = td_dict['days']
    _hours = td_dict['hours']
    _minutes = td_dict['minutes']
    _seconds = td_dict['seconds']
    return datetime.timedelta(days=_days, hours=_hours, minutes=_minutes, seconds=_seconds)


class MyJSONDecoder(json.JSONDecoder):
    '''
    classdocs
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, obj):
        if not '_type' in obj.keys():
            return obj
        _type = obj['_type']
        if _type == 'datetime':
            return _parse_datetime(obj['value'])
        elif _type == 'date':
            return _parse_date(obj['value'])
        elif _type == 'time':
            return _parse_time(obj['value'])
        elif _type == 'timedelta':
            return _parse_timedelta(obj['value'])
        return obj
