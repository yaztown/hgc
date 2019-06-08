'''
Created on Saturday 01/06/2019

@author: yaztown
'''

from flask import send_from_directory#, request, redirect, url_for
from hgc_net import flask_app

from . import api_routes


@flask_app.route('/')
def index():
    return flask_app.send_static_file('index.html')


@flask_app.route('/<path:path>')
def send_file(path):
    return send_from_directory(flask_app.static_folder, path)




# @flask_app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         user = request.form['nm']
#         return redirect(url_for('success', name = user))
#     else:
#         user = request.args.get('nm')
#         return redirect(url_for('success', name = user))
# 
# 
# @flask_app.route('/success/<name>')
# def success(name):
#     return 'Welcome {}'.format(name)
