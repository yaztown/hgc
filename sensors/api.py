'''
Created on Saturday 06/06/2019

@author: yaztown
'''

'''
Created on Sunday 02/06/2019

@author: yaztown
'''

from flask_jsonrpc import request
from hgc_net import flask_json_rpc, ResponseSuccess, ResponseError
from base_threads import BaseSensor
from hgc.core.json import dumps
from json import loads

# Global helper methods
def getSensor(uuid):
    return BaseSensor._get_instance_by_uuid(uuid)

getObject = getSensor

def getMethodFromRPCRequest(req):
    return req.get_json()['method'].split('.')[-1]

'''
RPC method definitions
'''

@flask_json_rpc.method('Sensor.list_sensors() -> Array')
def rpc_list_sensors(**kwargs):
    sensor_list = BaseSensor._get_instances(recursive=True)
    response = dumps(sensor_list)
    response = loads(response)
    return response


# def rpc_method_handler(**kwargs):
#     '''
#     This is a generic dispatcher that will call the requested rpc method with the params as kwargs 
#     '''
#     uuid = kwargs.pop('uuid', None)
#     if uuid is None: return ResponseError(err_msg='uuid is None')
#     obj = getObject(uuid=uuid)
#     if obj is None: return ResponseError(err_msg='No Controller matching uuid: {}'.format(uuid))
#     method = getMethodFromRPCRequest(request)
#     if not hasattr(obj, method): return ResponseError(err_msg='Method {} not defined in the requested object'.format(method))
#     try:
#         method_ret_value = getattr(obj, method)(**kwargs)
#     except:
#         return ResponseError(err_msg='method exception occurred')
#     return ResponseSuccess(success_msg='method: {}'.format(method), rpc_ret_value=method_ret_value)
# 
# 
# @flask_json_rpc.method('Controller.turn_on(uuid=String)')
# def rpc_turn_on(**kwargs):
#     '''
#     This method calls the turn_on() method to the controller
#     '''
#     return rpc_method_handler(**kwargs)
# 
# @flask_json_rpc.method('Controller.turn_off(uuid=String)')
# def rpc_turn_off(**kwargs):
#     '''
#     This method calls the turn_off() method to the controller
#     '''
#     return rpc_method_handler(**kwargs)
# 
# @flask_json_rpc.method('Controller.set_manual(uuid=String)')
# def rpc_set_manual(**kwargs):
#     '''
#     This method calls the set_manual() method to the controller
#     '''
#     return rpc_method_handler(**kwargs)
# 
# @flask_json_rpc.method('Controller.set_automatic(uuid=String)')
# def rpc_set_automatic(**kwargs):
#     '''
#     This method calls the set_automatic() method to the controller
#     '''
#     return rpc_method_handler(**kwargs)

