'''
Created on Saturday 01/06/2019

@author: yaztown
'''

from flask import Flask, request
from hgc_logging import get_logger
import os
from flask_jsonrpc import JSONRPC


WWW_FOLDER = 'www'

flask_host = '0.0.0.0'
flask_port = 8000

app_dir_path, _ = os.path.split(os.path.dirname(os.path.abspath(__file__)))
www_path = os.path.join(app_dir_path, WWW_FOLDER)


'''
the main flask app
'''
flask_app = Flask(__name__, static_url_path='', static_folder=www_path)
'''
the main flask json_rpc
'''
flask_json_rpc = JSONRPC(flask_app, '/api/jsonrpc')

'''
the main routes
'''
from hgc_net import routes


'''
the main server control methods
'''
def runServer(host=flask_host, port=flask_port, debug=False):
    flask_app.run(host=host, port=port, debug=debug)

def stopServer():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    shutdown_func()


'''
Standard Response objects
'''
def HGCResponse(success=True, success_msg='', err_msg='', err_code=0, rpc_ret_value=None):
    return dict(
        status='Success' if success else 'Error',
        success_msg=success_msg,
        err_msg=err_msg, err_code=err_code,
        rpc_ret_value=rpc_ret_value)

def ResponseSuccess(success_msg='', rpc_ret_value=None):
    return HGCResponse(success_msg=success_msg, rpc_ret_value=rpc_ret_value)

def ResponseError(err_msg='', err_code=-1, rpc_ret_value=None):
    return HGCResponse(success=False, err_msg=err_msg, err_code=err_code, rpc_ret_value=rpc_ret_value)
