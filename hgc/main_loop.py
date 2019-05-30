'''
Created on Friday 29/06/2018

@author: yaztown
'''

from netserve import HGCServer, SimpleHTTPAPIRequestHandler
from time import sleep
from pin_out import MyGPIO
from hgc_logging import get_logger
from base_threads import BaseThread

import sensors, device_controls

import threading


logger = get_logger()

class MainLoop(BaseThread):
    def __init__(self, setup_object={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mygpio = MyGPIO()
        self.sensors = []
        self.device_controls = []
        self.setup_object = setup_object.copy()
        self.httpd = None
        logger.debug('Initialized thread: {}'.format(self.name))
    
    def _setup_system(self):
        self._setup_sensors()
        self._setup_devices()
    
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
    
    def _setup_devices(self):
        devices_setup = self.setup_object.get('device_controls', []).copy()
        for device_setup in devices_setup:
            DeviceControlClass = None
            device = None
            class_name = device_setup.pop('class_name')
            
            if hasattr(device_controls, class_name):
                DeviceControlClass = getattr(device_controls, class_name)
            
            if DeviceControlClass is not None:
                device = DeviceControlClass(**device_setup)
                self.device_controls.append(device)
    
    def start_threads(self):
        for sensor in self.sensors:
            sensor.start()
        sleep(3)
        for device_control in self.device_controls:
            device_control.start()
    
    def start_server(self):
        '''
        This is the function that will start the server and return the httpd
        '''
        #TODO: move the following assignments to the settings file
        server_class = HGCServer
        handler_class = SimpleHTTPAPIRequestHandler
        HTTP_IP = '0.0.0.0'
        HTTP_PORT = 8000
        
        server_address = (HTTP_IP, HTTP_PORT)
        self.httpd = server_class(server_address, handler_class, self)
        print('Starting the server on address: http://{ip}:{port}'.format(ip=HTTP_IP, port=HTTP_PORT))
        try:
#             self.httpd.serve_forever()
            threading.Thread(target=self.httpd.serve_forever).start()
        except:
            pass
    
    #TODO: remove this start method since it clashes with the Thread classes method name
    def _setup_loop(self):
#         BaseThread._setup_loop(self)
        self._setup_system()
        self.start_threads()
        self.start_server()

    def __loop__(self):
#         logger.debug('from mainLoop __loop__()')
        sleep(2)
    
    def stop_threads(self):
        self.httpd.shutdown()
        for device_control in self.device_controls:
            device_control.stop()
            device_control.join()
        for sensor in self.sensors:
            sensor.stop()
            sensor.join()
    
    def clean_up(self):
        self.stop_threads()
        super().clean_up()
        
    def get_status(self):
        return True
