'''
Created on Sunday 02/06/2019

@author: yaztown
'''

from flask_jsonrpc import request
from hgc_net import flask_json_rpc, ResponseSuccess, ResponseError
from base_threads import BaseDeviceControl


def getController(uuid=None):
    return BaseDeviceControl._get_instance_by_uuid(uuid)


def getMethodFromRPCRequest(req):
    return req.get_json()['method'].split('.')[-1]



@flask_json_rpc.method('Controller.turn_on')
@flask_json_rpc.method('Controller.turn_off')
@flask_json_rpc.method('Controller.set_manual')
@flask_json_rpc.method('Controller.set_automatic')
def rpc_action(**kwargs):
    uuid = kwargs.pop('uuid', None)
    if uuid is None: return ResponseError(err_msg='uuid is None')
    controller = getController(uuid)
    if controller is None: return ResponseError(err_msg='No Controller matching uuid: {}'.format(uuid))
    method = getMethodFromRPCRequest(request)
    if not hasattr(controller, method): return ResponseError(err_msg='Method not defined in the requested object')
    try:
        method_ret_value = getattr(controller, method)(**kwargs)
    except:
        return ResponseError(err_msg='method exception occurred')
    return ResponseSuccess(success_msg='method: {}'.format(method), rpc_ret_value=method_ret_value)
