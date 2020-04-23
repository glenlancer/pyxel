#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import base64, re
from .connection import Connection

from .config import PYXEL_DEBUG

class Http(Connection):
    def __init__(
        self,
        ai_family, io_timeout, max_redirect, request_headers={},
        http_proxy=None, no_proxies=None, local_ifs=None):
        super(Http, self).__init__(ai_family, io_timeout, max_redirect, local_ifs)
        self.request_headers = request_headers
        self.response_headers = {}
        self.http_proxy = http_proxy
        self.no_proxies = no_proxies
        self.http_basic_auth = None
        self.request = None
        self.response = None
        self.resuming_supported = True

    def check_if_no_proxy(self):
        ''' If the target hostname is in no_procies list, then don\'t use proxy. '''
        for no_proxy in self.no_proxies:
            if self.hostname == no_proxy:
                self.http_proxy = None
                break

    def connect(self):
        host = self.host
        port = self.port
        user = self.user
        password = self.password
        if self.http_proxy:
            # Need to check how http_proxy actually works later.
            _, port, user, password, \
            host, _, _, _ \
                = self.analyse_url(self.http_proxy)
        if not self.tcp.connect(
            host,
            port,
            self.is_secure_scheme(),
            self.ai_family,
            self.io_timeout,
            self.local_ifs):
            return False
        self.http_basic_auth = None
        if user and password:
            self.basic_auth_token(user, password)
        return True

    def disconnect(self):
        self.tcp.close()

    def init(self):
        if self.url is None:
            raise Exception(f'Exception in {__name__}: set_url() needs to be called first.')
        self.check_if_no_proxy()
        if not self.connect():
            self.disconnect()
            return False
        return True

    def setup(self):
        if not self.is_connected():
            if not self.init():
                return False
        self.first_byte = -1
        if self.resuming_supported:
            self.first_byte = self.current_byte
        self.build_basic_get()
        self.http_additional_headers()
        return True

    def get_resource_info(self):
        redirect_count = 0
        while True:
            self.resuming_supported = True
            self.current_byte = 0
            if not self.setup() or not self.execute():
                return False, 'execute_failed'
            self.disconnect()
            self.set_filename_from_response()
            if self.status_code // 100 != 3:
                break
            # Following code needs to be tested thoroughly.
            redirect_count += 1
            if redirect_count > self.max_redirect:
                sys.stderr.write('Too many redirects.\n')
                return False, 'too_many_redirects'
            redirect_url = self.get_redirect_url_from_response()
            if redirect_url is None:
                return False
            self.set_url(redirect_url)
            if self.get_scheme_from_url(redirect_url) in (self.FTP, self.FTPS):
                return True, 'redirect_to_ftp'
        # Check for non-recoverable errors.
        if self.status_code != 416 and self.status_code // 100 != 2:
            return False, 'unrecoverable_errors'
        if self.set_filesize():
            return True, 'ok'
        return False, 'no_file_size'

    def execute(self):
        return self.send_get_request() and self.recv_get_response()

    def send_get_request(self):
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
        return True

    def recv_get_response(self):
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

    def basic_auth_token(self, user, password):
        self.http_basic_auth = base64.b64encode(f'{user}:{password}').strip()

    def build_basic_get(self):
        self.request = ''
        self.add_request_head()
        if self.http_basic_auth:
            self.add_header(f'Authorization: Basic %s' % (self.http_basic_auth))
        self.add_header('Accept: */*')
        self.add_range_header()

    def add_range_header(self):
        if self.first_byte >= 0 and self.last_byte:
            self.add_header('Range: bytes=%d-%d' % (self.first_byte, self.last_byte))
        else:
            self.add_header('Range: bytes=%d-' % (self.first_byte))

    def add_request_head(self):
        if self.http_proxy is None:
            self.add_header(f'GET %s%s HTTP/1.0' % (self.filedir, self.filename))
            if self.is_default_port(self.scheme, self.port):
                self.add_header(f'Host: %s' % (self.host))
            else:
                self.add_header(f'Host: %s:%d' % (self.host, self.port))
        else:
            proto_str = self.get_scheme(self.scheme)
            if self.is_default_port(self.port):
                get_str = ''.join([proto_str, self.host, self.filedir, self.filename])
            else:
                get_str = ''.joing([proto_str, self.host, self.filedir, self.filename])
            self.add_header('GET %s HTTP/1.0' % (get_str))

    def http_additional_headers(self):
        for key, value in self.request_headers.items():
            self.add_header(f'{key}: {value}')

    def add_header(self, header):
        self.request = ''.join([self.request, header, '\r\n'])

    def is_default_port(self, scheme, port):
        if scheme == self.HTTP:
            return port == self.HTTP_DEFAULT_PORT
        elif scheme == self.HTTPS:
            return port == self.HTTPS_DEFAULT_PORT
        else:
            raise Exception(f'Exception in {__name__}: Unknown scheme for Http.')

    def set_filesize(self):
        self.file_size = self.get_size_from_range()
        # We assume partial requests are supported if a Content-Range
        # header is present.
        self.resuming_supported = (self.status_code == 206) or (self.file_size > 0)
        if self.file_size <= 0:
            if self.status_code not in (200, 206, 416):
                return False
            self.resuming_supported = False
            self.file_size = self.MAX_FILESIZE
        else:
            self.file_size = max(self.file_size, self.get_size_from_length())
        return True

    def set_filename_from_response(self):
        filename = None
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
        if filename:
            self.output_filename = filename

    def get_size_from_length(self):
        if not 'Content-Length' in self.response_headers:
            return -1
        return int(self.response_headers['Content-Length'])

    def get_size_from_range(self):
        if not 'Content-Range' in self.response_headers:
            return None
        filesize = re.compile(
            '^.*/(.*)$'
        ).findall(self.response_headers['Content-Range'])[0]
        return int(filesize)

    def get_redirect_url_from_response(self):
        redirect_url = self.get_location_from_response()
        if redirect_url is None:
            return None
        elif redirect_url[0] == '/':
            return '%s%s:%i%s' % \
                (
                    self.get_scheme(self.scheme),
                    self.host,
                    self.port,
                    redirect_url
                )
        elif redirect_url.find('://') < 0:
            return ''.join([self.generate_url(), redirect_url])
        return redirect_url

    def get_location_from_response(self):
        if not 'location' in self.response_headers:
            return None
        return self.response_headers['location']