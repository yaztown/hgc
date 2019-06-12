'''
Created on Friday 29/06/2018

@author: yaztown
'''

# from netserve import HGCServer, SimpleHTTPAPIRequestHandler
from time import sleep
# from pin_out import MyGPIO
from hgc_logging import get_logger
from base_threads import BaseThread

# from hgc_net import routes, startFlaskServer, stopFlaskServer
from hgc_net import flask_app
from hgc_net.wsgiserver import WSThread

from . import routes

import sensors
import controllers

# import threading


logger = get_logger()

class MainLoop(BaseThread):
    def __init__(self, setup_object={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
#         _ = MyGPIO()
        self.sensors = []
        self.controllers = []
        self.setup_object = setup_object.copy()
        self.httpd = None
        logger.debug('Initialized thread: {}'.format(self.name))
    
    def _setup_system(self):
        self._setup_sensors()
        self._setup_controllers()
    
    def _setup_sensors(self):
        sensors_setup = self.setup_object.get('sensors', []).copy()
        for sensor_setup in sensors_setup:
            SensorClass = None
            sensor = None
            class_name = sensor_setup.pop('class_name')
            if hasattr(sensors, class_name):
                SensorClass = getattr(sensors, class_name)
            
            if SensorClass is not None:
                sensor = SensorClass(**sensor_setup)
                self.sensors.append(sensor)
    
    def _setup_controllers(self):
        controllers_setup = self.setup_object.get('controllers', []).copy()
        for controller_setup in controllers_setup:
            ControllerClass = None
            controller = None
            class_name = controller_setup.pop('class_name')
            
            if hasattr(controllers, class_name):
                ControllerClass = getattr(controllers, class_name)
            
            if ControllerClass is not None:
                controller = ControllerClass(**controller_setup)
                self.controllers.append(controller)
    
    def start_threads(self):
        for sensor in self.sensors:
            sensor.start()
        sleep(3)
        for controller in self.controllers:
            controller.start()
    
    def start_wsgiserver(self):
        self.httpd = WSThread(flask_app, name='wsgiserver')
        self.httpd.start()
    
    def _setup_loop(self):
        self._setup_system()
        self.start_threads()
        self.start_wsgiserver()

    def __loop__(self):
        sleep(2)
    
    def stop_wsgiserver(self):
        self.httpd.stop()
    
    def stop_threads(self):
        self.stop_wsgiserver()
        for controller in self.controllers:
            controller.stop()
            controller.join()
        for sensor in self.sensors:
            sensor.stop()
            sensor.join()
    
    def clean_up(self):
        self.stop_threads()
        super().clean_up()
        
    def get_status(self):
        return True
