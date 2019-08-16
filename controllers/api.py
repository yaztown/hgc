'''
Created on Sunday 02/06/2019

@author: yaztown
'''

from flask_jsonrpc import request
from hgc_net import flask_json_rpc, ResponseSuccess, ResponseError
from base_threads import BaseController
from hgc.core.json import dumps
from json import loads

# Global helper methods
def getController(uuid):
    return BaseController._get_instance_by_uuid(uuid)

def getMethodFromRPCRequest(req):
    return req.get_json()['method'].split('.')[-1]

'''
RPC method definitions
'''

@flask_json_rpc.method('Controller.list_controllers() -> Array')
def rpc_list_controllers(**kwargs):
    controller_list = BaseController._get_instances(recursive=True)
    response = dumps(controller_list)
    response = loads(response)
    return response

def rpc_method_handler(**kwargs):
    '''
    This is a generic dispatcher that will call the requested rpc method with the params as kwargs 
    '''
    uuid = kwargs.pop('uuid', None)
    if uuid is None: return ResponseError(err_msg='uuid is None')
    controller = getController(uuid=uuid)
    if controller is None: return ResponseError(err_msg='No Controller matching uuid: {}'.format(uuid))
    method = getMethodFromRPCRequest(request)
    if not hasattr(controller, method): return ResponseError(err_msg='Method not defined in the requested object')
    try:
        method_ret_value = getattr(controller, method)(**kwargs)
    except:
        return ResponseError(err_msg='method exception occurred')
    return ResponseSuccess(success_msg='method: {}'.format(method), rpc_ret_value=method_ret_value)


@flask_json_rpc.method('Controller.turn_on(uuid=String)')
def rpc_turn_on(**kwargs):
    '''
    This method calls the turn_on() method to the controller
    '''
    return rpc_method_handler(**kwargs)

@flask_json_rpc.method('Controller.turn_off(uuid=String)')
def rpc_turn_off(**kwargs):
    '''
    This method calls the turn_off() method to the controller
    '''
    return rpc_method_handler(**kwargs)

@flask_json_rpc.method('Controller.manual_turn_on(uuid=String)')
def rpc_manual_turn_on(**kwargs):
    '''
    This method calls the manual_turn_on() method to the controller
    this is a shortcut method
    '''
    return rpc_method_handler(**kwargs)

@flask_json_rpc.method('Controller.manual_turn_off(uuid=String)')
def rpc_manual_turn_off(**kwargs):
    '''
    This method calls the manual_turn_off() method to the controller
    this is a shortcut method
    '''
    return rpc_method_handler(**kwargs)

@flask_json_rpc.method('Controller.set_manual(uuid=String)')
def rpc_set_manual(**kwargs):
    '''
    This method calls the set_manual() method to the controller
    '''
    return rpc_method_handler(**kwargs)

@flask_json_rpc.method('Controller.set_automatic(uuid=String)')
def rpc_set_automatic(**kwargs):
    '''
    This method calls the set_automatic() method to the controller
    '''
    return rpc_method_handler(**kwargs)


@flask_json_rpc.method('Controller.config_controller(uuid=String, config_options=Object)')
def rpc_config_controller(**kwargs):
    '''
    This method calls the turn_on() method to the controller
    '''
    uuid = kwargs.pop('uuid', None)
    if uuid is None: return ResponseError(err_msg='uuid is None')
    controller = getController(uuid=uuid)
    if controller is None: return ResponseError(err_msg='No Controller matching uuid: {}'.format(uuid))
    try:
        config_options = kwargs['config_options']
        method_ret_value = controller.config_controller(**config_options)
    except:
        return ResponseError(err_msg='method exception occurred')
    return ResponseSuccess(success_msg='method: {}'.format('config_controller'), rpc_ret_value=method_ret_value)
 

# from . import api_timing