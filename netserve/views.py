'''
Created on Monday 11/03/2019

@author: yaztown
'''

from base_threads import BaseSensor, BaseDeviceControl
from hgc.core.json import HGCJSONEncoder, dumps


_json_indent = 4

def view_sensors(request={}, kwargs={}):
    if request['method'].upper() == 'GET':
        sensor_list = BaseSensor._get_instances(recursive=True)
        retval = dumps(sensor_list, indent=_json_indent)
        return retval
    elif request['method'].upper() == 'POST':
        return {}
    else:
        return 0

def view_sensor_by_name(request={}, kwargs={}):
    sensor_list = BaseSensor._get_instances(recursive=True)
    sensor = [sensor for sensor in sensor_list if sensor.name == kwargs['sensor_name']][0]
    retval = dumps(sensor, cls=HGCJSONEncoder, indent=_json_indent)
    return retval

def view_sensor_by_number(request={}, kwargs={}):
    pass


def view_controllers(request={}, kwargs={}):
    controller_list = BaseDeviceControl._get_instances(recursive=True)
    retval = dumps(controller_list, cls=HGCJSONEncoder, indent=_json_indent)
    return retval

def view_controller_by_name(request={}, kwargs={}):
    controller_list = BaseDeviceControl._get_instances(recursive=True)
    controller = [controller for controller in controller_list if controller.name == kwargs['controller_name']][0]
    return dumps(controller, cls=HGCJSONEncoder, indent=_json_indent)

def view_controller_by_number(request={}, kwargs={}):
    pass
