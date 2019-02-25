'''
Created on Monday 25/02/2019

@author: yaztown
'''
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

from urllib.parse import parse_qs

import json

__version__ = "0.0.1"

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class HGCServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass, mainLoop):
        super().__init__(server_address, RequestHandlerClass)
        self.mainLoop = mainLoop


class JSONAPIRequestHandler(BaseHTTPRequestHandler):
    '''
    classdocs
    '''
    
    server_version = "HGC_Server/" + __version__
    
    def write(self, message):
        if type(message).__name__ == 'str':
            self.wfile.write(bytes(message, 'UTF-8'))
        elif type(message).__name__ == 'bytes':
            self.wfile.write(message)
    
    def version_string(self):
        """Return the server software version string."""
        return self.server_version
    
    def do_GET(self):
        self.send_response(200)
        resp_ctype = 'text/html'
        self.send_header('Content-Type', resp_ctype)
        self.end_headers()
        reading_0 = self.server.mainLoop.sensors[0].get_reading()
        reading_1 = self.server.mainLoop.sensors[1].get_reading()
        page = '''
        <html>
        <body>
        <div>
            temp in: {}<br/> temp out: {}
        </div>
            <!--<form action="/" method="post">
                <input type="text" name="description" value="some text">
                <input type="password" name="passwd">
                <button type="submit">Submit</button>
            </form>-->
        </body>
        </html>
        '''.format(reading_0, reading_1)
        self.write(page)
    
    def do_POST(self):
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        qs = post_body.decode()
        print(qs)
        self.send_response(200)
        resp_ctype = 'application/json'
        self.send_header('Content-Type', resp_ctype)
        self.end_headers()
        self.write(json.dumps(parse_qs(qs, keep_blank_values=True), indent = 2))
