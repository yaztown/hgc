'''
Created on Sunday 02/06/2019

@author: yaztown
'''

from flask_jsonrpc import request
from hgc_net import flask_json_rpc, ResponseSuccess, ResponseError
from .timing_controllers import TimingController
from hgc.core.json import dumps
from json import loads

# Global helper methods
def getController(uuid):
    return TimingController._get_instance_by_uuid(uuid)

def getMethodFromRPCRequest(req):
    return req.get_json()['method'].split('.')[-1]

'''
RPC method definitions
'''

@flask_json_rpc.method('TimingController.timing_list_controllers() -> Array')
def rpc_timing_list_controllers(**kwargs):
    controller_list = TimingController._get_instances(recursive=True)
    response = dumps(controller_list)
    response = loads(response)
    return response


@flask_json_rpc.method('TimingController.timing_config_controller(time_on=Object, duration_on=Object, cycles_per_day=Number)')
def rpc_timing_config_controller(**kwargs):
    '''
    This method calls the turn_on() method to the controller
    '''
    uuid = kwargs.pop('uuid', None)
    if uuid is None: return ResponseError(err_msg='uuid is None')
    controller = getController(uuid=uuid)
    if controller is None: return ResponseError(err_msg='No Controller matching uuid: {}'.format(uuid))
    try:
        method_ret_value = controller.config_controller(**kwargs)
    except:
        return ResponseError(err_msg='method exception occurred')
    return ResponseSuccess(success_msg='method: {}'.format('timing_config_controller'), rpc_ret_value=method_ret_value)
 
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

