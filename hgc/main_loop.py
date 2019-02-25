'''
Created on Friday 29/06/2018

@author: yaztown
'''

from netserve import HGCServer, JSONAPIRequestHandler

from base_threads import BaseThread
# from sensors import HumidityTemperatureSensor
# from device_controls import DeviceTimingControl, DeviceHumTempSensorControl, DeviceSensorsCompareControl
import sensors, device_controls

from time import sleep


class MainLoop(BaseThread):
    def __init__(self, setup_object={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sensors = []
        self.device_controls = []
        self.setup_object = setup_object.copy()
        self._setup_system()
    
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
    
    def setup_logic(self):
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
        handler_class = JSONAPIRequestHandler
        HTTP_IP = '0.0.0.0'
        HTTP_PORT = 8000
        
        server_address = (HTTP_IP, HTTP_PORT)
        httpd = server_class(server_address, handler_class, self)
        print('Starting the server on address: http://{ip}:{port}'.format(ip=HTTP_IP, port=HTTP_PORT))
        httpd.serve_forever()
    
    def start(self):
        self.setup_logic()
        self.start_server()
        super().start()
    
    def get_status(self):
        return True

    def __work__(self):
        sleep(2)
