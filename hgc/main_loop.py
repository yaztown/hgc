'''
Created on Friday 29/06/2018

@author: yaztown
'''

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
