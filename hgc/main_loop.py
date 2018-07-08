'''
Created on Friday 29/06/2018

@author: yaztown
'''

from base_threads import BaseThread
from sensors import HumidityTemperatureSensor
from device_controls import DeviceTimingControl, DeviceHumTempSensorControl, DeviceSensorsCompareControl
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
            sensor_type = sensor_setup.pop('sensor_type')
            if sensor_type == 'HumidityTemperatureSensor':
                SensorClass = HumidityTemperatureSensor
            sensor = SensorClass(**sensor_setup)
            
            if sensor is not None:
                self.sensors.append(sensor)
#                 sensor.start()
    
    def _setup_devices(self):
        devices_setup = self.setup_object.get('device_controls', []).copy()
        for device_setup in devices_setup:
            DeviceControlClass = None
            device_control_type = device_setup.pop('device_control_type')
            if device_control_type == 'DeviceTimingControl':
                DeviceControlClass = DeviceTimingControl
            elif device_control_type == 'DeviceHumTempSensorControl':
                DeviceControlClass = DeviceHumTempSensorControl
            elif device_control_type == 'DeviceSensorsCompareControl':
                DeviceControlClass = DeviceSensorsCompareControl
            device = DeviceControlClass(**device_setup)
            
            if device is not None:
                self.device_controls.append(device)
    
    def setup_logic(self):
        for sensor in self.sensors:
            sensor.start()
        sleep(3)
        for device_control in self.device_controls:
            device_control.start()
    
    def start(self):
        self.setup_logic()
        super().start()
    
    def get_status(self):
        return True

    def __work__(self):
        sleep(2)

# if __name__ == '__main__':
#     main_loop = MainLoop(setup_object=SETUP_OBJECT, name='main_loop', loop_sleep_time=1)
#     main_loop.start()
#     
#     while True:
#         if not main_loop.get_status():
#             raise Exception()
#         sleep(2)
