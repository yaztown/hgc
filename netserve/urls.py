'''
Created on Monday 11/03/2019

@author: yaztown
'''
from .views import view_sensors, view_sensor_by_name, \
                   view_controllers, view_controller_by_name

urls_conf = [
        (r'^/api/sensors/?$', view_sensors),
        (r'^/api/sensors/(?P<sensor_name>[a-z]\w+)/?$', view_sensor_by_name),
#         (r'/api/sensors/(?P<sensor_number>\d+)/?$', view_sensor_by_number), 
        (r'^/api/controllers/?$', view_controllers),
        (r'^/api/controllers/(?P<controller_name>[a-z]\w+)/?$', view_controller_by_name),
#         (r'^/api/controllers/(?P<controller_number>\d+)/?$', view_controller_by_number), 
    ]
