'''
Created on Monday 25/02/2019

@author: yaztown
'''
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

from urllib.parse import parse_qs

import json, urllib, os, posixpath

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
        <table>
            <tr>
                <td></td><td>temp</td><td>humd</td>
            </tr>
            <tr>
                <td>in</td><td>{temp_in:.1f}</td><td>{humidity_in:.1f}</td>
            </tr>
            <tr>
                <td>out</td><td>{temp_out:.1f}</td><td>{humidity_out:.1f}</td>
            </tr>
        </table>
        </div>
        </body>
        </html>
        '''.format(**{
            'temp_in': reading_0['temperature'],
            'temp_out':reading_1['temperature'],
            'humidity_in': reading_0['humidity'],
            'humidity_out':reading_1['humidity']
            })
        self.write(page)
    
    def test_handle_api_request(self):
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
        <table>
            <tr>
                <td></td><td>temp</td><td>humd</td>
            </tr>
            <tr>
                <td>in</td><td>{temp_in:.1f}</td><td>{humidity_in:.1f}</td>
            </tr>
            <tr>
                <td>out</td><td>{temp_out:.1f}</td><td>{humidity_out:.1f}</td>
            </tr>
        </table>
        </div>
        </body>
        </html>
        '''.format(**{
            'temp_in': reading_0['temperature'],
            'temp_out':reading_1['temperature'],
            'humidity_in': reading_0['humidity'],
            'humidity_out':reading_1['humidity']
            })
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




from netserve.simple_url_handler import SimpleURLHandler

class SimpleHTTPAPIRequestHandler(SimpleHTTPRequestHandler):
    '''
    classdocs
    '''
    server_version = "HGC_Server/" + __version__
    www_dir = 'www'
    
    @property
    def method(self):
        return self.command
    
    def version_string(self):
        """Return the server software version string."""
        return self.server_version
    
    def write(self, message):
        if type(message).__name__ == 'str':
            self.wfile.write(bytes(message, 'UTF-8'))
        elif type(message).__name__ == 'bytes':
            self.wfile.write(message)
    
    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd() + '/' + self.www_dir
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path
    
    def handle_api_request(self):
        api_request = {
            'path': self.path,
            'method': self.method,
            'full_request': self
        }
        handler = SimpleURLHandler(request=api_request)
        page_str = handler.handle()
        self.write_page(page_str=page_str, resp_ctype='application/json')
    
    def do_GET(self):
#         print(self.path)
        if self.path.startswith('/api'):
            self.handle_api_request()
        else:
            super().do_GET()
    
    def do_OPTIONS(self):
        #
        headers = {}
        headers.update({'Access-Control-Allow-Origin': '*'})
        headers.update({'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'}) 
        headers.update({'Access-Control-Allow-Headers': 'Content-Type'})
        headers.update({'Access-Control-Max-Age': '86400'})
#         headers.update({'Keep-Alive': 'timeout=2, max=100'})
#         headers.update({'Connection': 'Keep-Alive'})
#         headers.update({'Content-Length': '0'})
        return self.write_page(headers=headers)
        
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
    
    def write_page(self, page_str='', resp_ctype='text/plain', headers={}):
        self.send_response(200)
        self.send_header('Content-Type', resp_ctype)
        headers.update({'Access-Control-Allow-Origin': '*'})
        headers.update({'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'}) 
        headers.update({'Access-Control-Allow-Headers': 'Content-Type'})
        headers.update({'Access-Control-Max-Age': '86400'})
        for hk, hv in headers.items():
            self.send_header(hk, hv)
        self.end_headers()
        self.write(page_str)
