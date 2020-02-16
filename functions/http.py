#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import base64, re
from .connection import Connection

from .config import PYXEL_DEBUG

class Http(Connection):
    def __init__(self, ai_family, io_timeout, headers={}, http_proxy=None, no_proxies=None, local_ifs=None):
        super(Http, self).__init__(ai_family, io_timeout, local_ifs)
        self.headers = headers
        self.response_headers = {}
        self.http_proxy = http_proxy
        self.no_proxies = no_proxies
        self.http_basic_auth = None
        self.supported = True
        self.current_byte = 0
        self.request = ''
        self.response = ''
        self.first_byte = 0
        self.last_byte = 0

    def check_http_proxy(self):
        for no_proxy in self.no_proxies:
            if self.hostname == no_proxy:
                self.http_proxy = None
                break

    def init(self, url):
        if self.url_info == {}:
            self.set_url(url, Connection.TARGET_URL)
        self.check_http_proxy()
        if not self.connect():
            self.disconnect()
            return False
        return True

    def set_filename_from_response(self):
        if not 'Content-Disposition' in self.response_headers:
            return
        # This regex needs to be improved.
        filename = re.compile(
            '^.*filename=[\'\"](.*)[\'\"]$'
        ).findall(self.response_headers['Content-Disposition'])[0]
        # Replace common invalid characters in filename
	    # https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words
        for char in '/\\?%*:|<>':
            filename = filename.replace('_', char)
        self.output_filename = filename

    def get_info(self):
        if not self.is_connected():
            raise Exception(f'Exception in {__name__}: init() needs to be called first.')
        while True:
            self.supported = True
            self.current_byte = 0
            self.setup()
            self.execute()
            self.disconnect()
            self.set_filename_from_response()
            if self.status_code // 100 != 3:
                break
            

    def setup(self):
        self.first_byte = -1
        if self.supported:
            self.first_byte = self.current_byte
        self.http_basic_get()
        self.http_additional_headers()

    def execute(self):
        if PYXEL_DEBUG:
            sys.stderr.write('--- Sending request ---\n')
            sys.stderr.write(self.request)
            sys.stderr.write('--- End of request ---\n')
        self.request = ''.join([self.request, '\r\n'])
        try:
            self.tcp.send(self.request.encode('utf-8'))
        except RuntimeError as r:
            sys.stderr.write(f'{r.message}\n')
            return False
        # Read the headers byte by byte.
        first_newline = True
        self.response = ''
        while True:
            try:
                recv_char = self.tcp.recv(1).decode('utf-8')
            except RuntimeError as r:
                sys.stderr.write(f'{r.message}\n')
                return False
            if recv_char == '\r':
                continue
            elif recv_char == '\n':
                if not first_newline:
                    break
                else:
                    first_newline = False
            else:
                first_newline = True
            self.response += recv_char
        if PYXEL_DEBUG:
            sys.stderr.write('--- Reply headers ---\n')
            sys.stderr.write(self.response)
            sys.stderr.write('--- End of headers ---\n')
        response_lines = self.response.split('\n')
        self.status_code = int(response_lines[0].split(' ')[1])
        for line in response_lines[1:]:
            if line == '':
                continue
            [key, value] = line.split(': ')
            self.response_headers[key] = value
        return self.status_code // 100 == 2

    def connect(self):
        url_type = Connection.TARGET_URL
        if self.http_proxy is not None:
            self.set_url(self.http_proxy, Connection.HTTP_PROXY_URL)
            url_type = Connection.HTTP_PROXY_URL
        if not self.tcp.connect(
            self.url_info[url_type]['hostname'],
            self.url_info[url_type]['port'],
            self.is_secure_scheme(self.url_info[url_type]['scheme']),
            self.ai_family,
            self.io_timeout,
            self.local_ifs):
            return False
        if self.url_info[url_type]['user'] and self.url_info[url_type]['password']:
            self.basic_auth_token(
                self.url_info[url_type]['user'], self.url_info[url_type]['password']
            )
        return True

    def disconnect(self):
        self.tcp.close()

    def basic_auth_token(self, user, password):
        self.http_basic_auth = base64.b64encode(f'{user}:{password}').strip()

    def http_basic_get(self):
        self.request = ''
        info = self.url_info[Connection.TARGET_URL]
        if self.http_proxy is None:
            self.add_header(f'GET %s%s HTTP/1.0' % (info['file_dir'], info['file']))
            if self.is_default_port(info['scheme'], info['port']):
                self.add_header(f'Host: %s' % (info['hostname']))
            else:
                self.add_header(f'Host: %s:%d' % (info['hostname'], info['port']))
        else:
            proto_str = Connection.get_scheme(info['scheme'])
            if self.is_default_port(info['port']):
                get_str = ''.join([proto_str, info['hostname'], info['file_dir'], info['file']])
            else:
                get_str = ''.joing([proto_str, info['hostname'], info['file_dir'], info['file']])
            self.add_header('GET %s HTTP/1.0' % (get_str))
        if self.http_basic_auth:
            self.add_header(f'Authorization: Basic %s' % (self.http_basic_auth))
        self.add_header('Accept: */*')
        if self.first_byte >= 0:
            if self.last_byte:
                self.add_header('Range: bytes=%d-%d' % (self.first_byte, self.last_byte))
            else:
                self.add_header('Range: bytes=%d-' % (self.first_byte))

    def http_additional_headers(self):
        for key, value in self.headers.items():
            self.add_header(f'{key}: {value}')

    def add_header(self, new_header):
        self.request = ''.join([self.request, new_header, '\r\n'])

    def is_default_port(self, scheme, port):
        if scheme == Connection.HTTP:
            return port == Connection.HTTP_DEFAULT_PORT
        elif scheme == Connection.HTTPS:
            return port == Connection.HTTPS_DEFAULT_PORT
        else:
            raise Exception(f'Exception in {__name__}: Unknown scheme for Http.')