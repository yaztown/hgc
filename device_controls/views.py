'''
Created on Saturday 01/06/2019

@author: yaztown
'''

from flask import request, Response
from hgc_net import flask_app, flask_json_rpc
from hgc.core.json import dumps
from base_threads import BaseDeviceControl


_json_indent = 4


@flask_app.route('/api/controllers')
def api_list_controllers():
    '''
    view_controllers(request={}, kwargs={}):
    '''
    controller_list = BaseDeviceControl._get_instances(recursive=True)
    response = dumps(controller_list, indent=_json_indent)
#     return retval
    return Response(response, 200, mimetype="application/json")


@flask_app.route('/api/controllers/<name>')
def api_get_controller_by_name(name):
    controller_list = BaseDeviceControl._get_instances(recursive=True)
    controller = [controller for controller in controller_list if controller.name == name][0]
    response = dumps(controller, indent=_json_indent)
    return Response(response, 200, mimetype="application/json")


@flask_app.route('/api/controllers/uuid/<uuid>')
def api_get_controller_by_uuid(uuid):
    controller_list = BaseDeviceControl._get_instances(recursive=True)
    controller = [controller for controller in controller_list if controller.uuid == uuid][0]
    response = dumps(controller, indent=_json_indent)
    return Response(response, 200, mimetype="application/json")



# @flask_app.route('/api/rpc', methods = ['POST'])
# def rpc():
#     req = request.get_data().decode()
#     
#     response = {'name': 'yaztown'}
#     return Response(str(response), response.http_status, mimetype="application/json")
# 
# from jsonrpcserver import method, dispatch
# 
# @method
# def ping():
#     return 'pong'
# 
# @flask_app.route('/api/json_rpc', methods=['POST'])
# def json_rpc():
#     req = request.get_data().decode()
#     response = dispatch(req)
#     return Response(str(response), response.http_status, mimetype='application/json')
