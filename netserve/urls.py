'''
Created on Monday 11/03/2019

@author: yaztown
'''
from .views import get_sensors, get_sensor_by_name, \
                   get_controllers, get_controller_by_name

urls_conf = [
        (r'^/api/sensors/?$', get_sensors),
        (r'^/api/sensors/(?P<sensor_name>[a-z]\w+)/?$', get_sensor_by_name),
#         (r'/api/sensors/(?P<sensor_number>\d+)/?$', get_sensor_by_number), 
        (r'^/api/controllers/?$', get_controllers),
        (r'^/api/controllers/(?P<controller_name>[a-z]\w+)/?$', get_controller_by_name),
#         (r'^/api/controllers/(?P<controller_number>\d+)/?$', get_controller_by_number), 
    ]
