'''
Created on Tuesday 03/07/2018

@author: yaztown
'''

from datetime import time, timedelta


HGC_SETUP = {
    'sensors': [
        dict(name='hum_temp_dht_22_in',
             sensor_type='HumidityTemperatureSensor',
             data_pin=4,    # 7
             save_data=True),
        dict(name='hum_temp_dht_22_out',
             sensor_type='HumidityTemperatureSensor',
             data_pin=17,   # 11
             save_data=True),
    ],
    # TODO: Think of replacing the dict objects into a class with a meta pointing to the write subclass
    'device_controls': [
        dict(name='light_control',
             device_control_type='DeviceTimingControl',
             relay_pin=[5, 6],  # 29, 31
             time_on=time(15),
             duration_on=timedelta(hours=18),
             cycles_per_day=1),
        dict(name='irrigation_control',
             device_control_type='DeviceTimingControl',
             relay_pin=[22, 27],    # 15, 13
             time_on=time(14,57),
             duration_on=timedelta(seconds=50),
             cycles_per_day=0.5),
        dict(name='exhaust_fan_control',
             device_control_type='DeviceHumidityCompareControl',
             relay_pin=[23, 24],    # 16, 18
             sensor_in_name='hum_temp_dht_22_in',
             sensor_out_name='hum_temp_dht_22_out',
             threshold_humidity_upper=65,
             ),
        dict(name='intake_fan_control',
             device_control_type='DeviceTempCompareControl',
             relay_pin=[16, 26],    # 36, 37
             sensor_in_name='hum_temp_dht_22_in',
             sensor_out_name='hum_temp_dht_22_out',
             threshold_temp_upper=27,
             ),
    ],
}


HGC_SETUP_TEST = {
    'sensors': [
        dict(name='hum_temp_dht_22',
             sensor_type='HumidityTemperatureSensor',
             data_pin=4,
             save_data=True)
    ],
    'device_controls': [
        dict(name='light_control',
             device_control_type='DeviceTimingControl',
             relay_pin=5,
             time_on=time(14),
             duration_on=timedelta(minutes=5),
             cycles_per_day=144),
        dict(name='irrigation_control',
             device_control_type='DeviceTimingControl',
             relay_pin=6,
             time_on=time(14),
             duration_on=timedelta(minutes=10),
             cycles_per_day=96),
        dict(name='exhaust_fan_control',
             device_control_type='DeviceHumTempSensorControl',
             relay_pin=7,
             sensor_name='hum_temp_dht_22',
             threshold_humidity_upper=60,
             threshold_humidity_lower=50,
             threshold_temp_upper=27,
             threshold_temp_lower=23
             ),
    ],
}
