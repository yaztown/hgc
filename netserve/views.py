'''
Created on Monday 11/03/2019

@author: yaztown
'''

from base_threads import BaseSensor, BaseDeviceControl
from hgc.core.json import HGCJSONEncoder, dumps


_json_indent = 4

def get_sensors(kwargs):
    sensor_list = BaseSensor._get_instances(recursive=True)
    retval = dumps(sensor_list, indent=_json_indent)
    return retval

def get_sensor_by_name(kwargs):
    sensor_list = BaseSensor._get_instances(recursive=True)
    sensor = [sensor for sensor in sensor_list if sensor.name == kwargs['sensor_name']][0]
    retval = dumps(sensor, cls=HGCJSONEncoder, indent=_json_indent)
    return retval

def get_sensor_by_number(kwargs):
    pass


def get_controllers(kwargs):
    controller_list = BaseDeviceControl._get_instances(recursive=True)
    retval = dumps(controller_list, cls=HGCJSONEncoder, indent=_json_indent)
    return retval

def get_controller_by_name(kwargs):
    controller_list = BaseDeviceControl._get_instances(recursive=True)
    controller = [controller for controller in controller_list if controller.name == kwargs['controller_name']][0]
    return dumps(controller, cls=HGCJSONEncoder, indent=_json_indent)

def get_controller_by_number(kwargs):
    pass
