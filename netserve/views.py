'''
Created on Thursday 07/03/2019

@author: yaztown
'''

from netserve.response import HttpResponse, JsonResponse

from sensors import HumidityTemperatureSensor
from device_controls import DeviceHumidityCompareControl, DeviceTempCompareControl, DeviceTimingControl

class HGC_View(object):
    '''
    classdocs
    '''
    model_class = None
    
    def __init__(self, request=None, response_class=HttpResponse):
        '''
        Constructor
        '''
        self.request = request
        self.response = response_class
    
    @classmethod
    def as_view(cls):
        pass
    
    def get_model_class(self):
        return self.model_class


import json

class HGC_List_View(HGC_View):
    @classmethod
    def as_view(cls, request=None):
        view = cls(request=request)
        # TODO: add the get_list method to the devices and sensors bases classes
        return json.dumps(view.model_class.get_list())

class HGC_Detail_View(HGC_View):
    @classmethod
    def as_view(cls, request=None, id_tag='id'):
        view = cls(request=request)
        # TODO: add the get_item_id method to the devices and sensors bases classes
        return json.dumps(view.model_class.get_item_id(id))


class HGC_Sensor_List_View(HGC_List_View):
    model_class = HumidityTemperatureSensor

class HGC_Sensor_Detail_View(HGC_Detail_View):
    model_class = HumidityTemperatureSensor


class HGC_Timing_Controller_List_View(HGC_List_View):
    model_class = DeviceTimingControl

class HGC_Timing_Controller_Detail_View(HGC_Detail_View):
    model_class = DeviceTimingControl


class HGC_HumidityCompare_Controller_List_View(HGC_List_View):
    model_class = DeviceHumidityCompareControl

class HGC_HumidityCompare_Controller_Detail_View(HGC_Detail_View):
    model_class = DeviceHumidityCompareControl


class HGC_TempCompare_Controller_List_View(HGC_List_View):
    model_class = DeviceTempCompareControl

class HGC_TempCompare_Controller_Detail_View(HGC_Detail_View):
    model_class = DeviceTempCompareControl

