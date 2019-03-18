'''
Created on Thursday 07/03/2019

@author: yaztown
'''

from .response import HttpResponse, HttpResponseNotAllowed, Http404
from .mixins import MultipleObjectMixin, JSONResponseMixin

from sensors import HumidityTemperatureSensor
from device_controls import DeviceHumidityCompareControl, DeviceTempCompareControl, DeviceTimingControl

from functools import update_wrapper

import logging

logger = logging.getLogger('netserve.request')



class classonlymethod(classmethod):
    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError("This method is available only on the class, not on instances.")
        return super(classonlymethod, self).__get__(instance, cls)


class View(object):
    """
    Intentionally simple parent class for all views. Only implements
    dispatch-by-method and simple sanity checking.
    """

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classonlymethod
    def as_view(cls, **initkwargs):
        """
        Main entry point for a request-response process.
        """
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        view.view_initkwargs = initkwargs

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())
        return view

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning(
            'Method Not Allowed (%s): %s', request.method, request.path,
            extra={'status_code': 405, 'request': request}
        )
        return HttpResponseNotAllowed(self._allowed_methods())

    def options(self, request, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """
        response = HttpResponse()
        response['Allow'] = ', '.join(self._allowed_methods())
        response['Content-Length'] = '0'
        return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


class BaseListView(MultipleObjectMixin, View):
    """
    A base view for displaying a list of objects.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)

class ListView(JSONResponseMixin, BaseListView):
    """
    Render some list of objects, set by `self.model` or `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    """

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

