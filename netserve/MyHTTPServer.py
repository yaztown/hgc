'''
Created on Thursday 26/07/2018

@author: yaztown
'''
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer

from urllib.parse import parse_qs

import json


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class SimpleAPIRequestHandler(SimpleHTTPRequestHandler):
    '''
    classdocs
    '''
    def write(self, message):
        if type(message).__name__ == 'str':
            self.wfile.write(bytes(message, 'UTF-8'))
        elif type(message).__name__ == 'bytes':
            self.wfile.write(message)
    def handle_api_request(self):
        pass
    def do_GET(self):
        print(self.path)
        if self.path.endswith('/api'):
            self.handle_api_request()
        else:
            super().do_GET()
    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        qs = post_body.decode()
        print(qs)
        self.send_response(200)
        json_ct = 'application/json'
        self.send_header('Content-Type', json_ct)
        self.end_headers()
        self.write(json.dumps(parse_qs(qs, keep_blank_values=True), indent = 2))

class JSONAPIRequestHandler(BaseHTTPRequestHandler):
    '''
    classdocs
    '''
    def write(self, message):
        if type(message).__name__ == 'str':
            self.wfile.write(bytes(message, 'UTF-8'))
        elif type(message).__name__ == 'bytes':
            self.wfile.write(message)
    def do_GET(self):
        self.send_response(200)
        json_ct = 'application/json'
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        page = '''
        <form action="/" method="post">
        <input type="text" name="description" value="some text">
        <input type="password" name="passwd">
        <button type="submit">Submit</button>
        </form>
        '''
        self.write(page)
        #self.wfile.write(bytes('You have requested ' + self.path + '\n', 'UTF-8'))
    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        qs = post_body.decode()
        print(qs)
        self.send_response(200)
        json_ct = 'application/json'
        self.send_header('Content-Type', json_ct)
        self.end_headers()
        self.write(json.dumps(parse_qs(qs, keep_blank_values=True), indent = 2))
        
def run_server(server_class=ThreadingHTTPServer, handler_class=BaseHTTPRequestHandler, HTTP_IP='0.0.0.0', HTTP_PORT=8000):
    server_address = (HTTP_IP, HTTP_PORT)
    httpd = server_class(server_address, handler_class)
    print('Starting the server on address: http://{ip}:{port}'.format(ip=HTTP_IP, port=HTTP_PORT))
    httpd.serve_forever()

def start_dev_server():
    run_server(server_class=ThreadingHTTPServer, handler_class=SimpleAPIRequestHandler)

if __name__ == '__main__':
    start_dev_server()

"""
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from http.server import SimpleHTTPRequestHandler
import json

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
 server_address = ('', 8000)
 httpd = server_class(server_address, handler_class)
 httpd.serve_forever()

class MyHandlerForHTTP(BaseHTTPRequestHandler):
    def write(self, message):
        if type(message).__name__ == 'str':
            self.wfile.write(bytes(message, 'UTF-8'))
        elif type(message).__name__ == 'bytes':
            self.wfile.write(message)
        else:
            pass
    def dogetorig(self):
        self.send_response(200)
        json_ct = 'application/json'
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(bytes('', 'UTF-8'))
        self.wfile.write(bytes('You have requested ' + self.path + '\n', 'UTF-8'))
    
    def do_GET(self):
        self.send_response(200)
        json_ct = 'application/json'
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        page = '''
        <form action="/" method="post">
        <input type="text" name="description" value="some text">
        <input type="password" name="passwd">
        <button type="submit">Submit</button>
        </form>
        '''
        self.write(page)
        self.wfile.write(bytes('You have requested ' + self.path + '\n', 'UTF-8'))
    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        type(post_body)
        print(post_body)
        self.send_response(200)
        json_ct = 'application/json'
        self.send_header('Content-Type', json_ct)
        self.end_headers()
        self.wfile.write(post_body)

run(handler_class=MyHandlerForHTTP)
"""