#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import base64
import re

from .connection import Connection

from .config import PYXEL_DEBUG
from .config import is_filename_valid

class Http(Connection):
    def __init__(
        self,
        ai_family, io_timeout, max_redirect, request_headers={},
        http_proxy=None, no_proxies=None, local_ifs=None):
        super(Http, self).__init__(ai_family, io_timeout, max_redirect, local_ifs)
        self.http_proxy = http_proxy
        self.no_proxies = no_proxies
        self.http_basic_auth = None
        self.use_http_proxy = True
        self.response = None
        self.request_headers = request_headers
        self.response_headers = {}
        self.resuming_supported = False

    def check_if_no_proxy(self):
        '''
        If the target hostname is in no_proxies list, then don\'t use proxy.
        Reviewed on 5/21/2020
        '''
        if self.host in self.no_proxies:
            self.use_http_proxy = False

    def connect(self):
        ''' Estabilish a Tcp connection to the host ''' 
        host = self.host
        port = self.port
        user = self.user
        password = self.password
        self.check_if_no_proxy()
        if self.use_http_proxy and self.http_proxy:
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

    def connection_init(self):
        assert self.url is not None, 'set_url() needs to be called first.'
        if not self.connect():
            self.disconnect()
            return False
        return True

    def request_setup(self):
        assert self.is_connected(), 'connection needs to be estabilished first, call connection_init().'
        self.first_byte = -1
        if self.resuming_supported:
            self.first_byte = self.current_byte
        self.build_basic_get()
        self.http_additional_headers()
        return True

    def get_resource_info(self):
        self.redirect_to_ftp = False
        redirect_count = 0
        while True:
            self.resuming_supported = True
            self.current_byte = 0
            if not self.request_setup() or not self.execute_req_resp():
                return False
            self.disconnect()
            self.set_filename_from_response()
            # Code 3xx == redirect.
            if self.status_code // 100 != 3:
                break
            # Following code needs to be tested thoroughly.
            redirect_count += 1
            if redirect_count > self.max_redirect:
                sys.stderr.write('Too many redirects.\n')
                return False
            redirect_url = self.get_redirect_url_from_response()
            if redirect_url is None:
                return False
            self.set_url(redirect_url)
            # Redirect to Ftp.
            if self.get_scheme_from_url(redirect_url) in (self.FTP, self.FTPS):
                self.redirect_to_ftp = True
                return True
        # Check for non-recoverable errors.
        if self.status_code != 416 and self.status_code // 100 != 2:
            return False
        if self.set_filesize():
            return True
        return False

    def execute_req_resp(self):
        return self.send_get_request() and self.recv_get_response()

    def send_get_request(self):
        if PYXEL_DEBUG:
            sys.stdout.write('--- Sending request ---\n')
            sys.stdout.write(self.request)
            sys.stdout.write('--- End of request ---\n')
        # Adding an empty line to indicate the end of the header fields.
        # Message-body is optional.
        self.request = ''.join([self.request, '\r\n'])
        try:
            self.tcp.send(self.request.encode('utf-8'))
        except Exception as e:
            sys.stderr.write(f'{e.args[-1]}\n')
            return False
        return True

    def recv_get_response(self):
        # Read the headers byte by byte.
        first_newline = True
        self.response = ''
        while True:
            try:
                recv_char = self.tcp.recv(1).decode('utf-8')
            except Exception as e:
                sys.stderr.write(f'{e.args[-1]}\n')
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
        self.add_request_line()
        if self.http_basic_auth:
            self.add_header(f'Authorization: Basic {self.http_basic_auth}')
        self.add_header('Accept: */*')
        self.add_range_header()

    def add_range_header(self):
        if self.first_byte < 0 or self.last_byte < 0:
            raise Exception(f'first_byte and last_byte must be >= 0, actual value is {self.first_byte}-{self.last_byte}')
        if self.last_byte > 0:
            self.add_header('Range: bytes={}-{}'.format(self.first_byte, self.last_byte))
        else:
            self.add_header('Range: bytes={}-'.format(self.first_byte))

    def add_request_line(self):
        '''
        The Request-Line begins with a method token, followed by the Request-URI and the
        protocol version, and ending with CRLF. The elements are separated by space SP
        characters.
        Request-Line = Method SP Request-URI SP HTTP-Version CRLF.
        '''
        if self.http_proxy:
            proto_str = self.get_scheme_str(self.scheme)
            if Http.is_default_port(self.scheme, self.port):
                get_str = ''.join([proto_str, self.host, self.filedir, self.filename])
            else:
                get_str = ''.join([proto_str, self.host, ':', self.port, self.filedir, self.filename])
            self.add_header(f'GET {get_str} HTTP/1.0')
        else:
            self.add_header(f'GET {self.filedir}{self.filename} HTTP/1.0')
            if Http.is_default_port(self.scheme, self.port):
                self.add_header(f'Host: {self.host}')
            else:
                self.add_header(f'Host: {self.host}:{self.port}')

    def http_additional_headers(self):
        for key, value in self.request_headers.items():
            self.add_header(f'{key}: {value}')

    def add_header(self, header):
        '''
        A header field followed by a CRLF.
        '''
        self.request = ''.join([self.request, header, '\r\n'])

    def set_filesize(self):
        self.file_size = self.get_size_from_range()
        # We assume partial requests are supported if a Content-Range header is present.
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
        '''
        Example: Content-Disposition: attachment; filename="filename.jpg"
        '''
        if not 'Content-Disposition' in self.response_headers:
            content_disposition = 'Content-Disposition'
        elif not 'content-disposition' in self.response_headers:
            content_disposition = 'content-disposition'
        else:
            return

        filename = re.compile(
            '^.*filename=[\'\"](.*)[\'\"]$'
        ).findall(self.response_headers[content_disposition])[0]
        # Replace common invalid characters in filename
        # https://en.wikipedia.org/wiki/Filename#Reserved_characters_and_words
        for char in '/\\?%*:|<>':
            filename = filename.replace('_', char)
            if not is_filename_valid(filename):
                raise Exception(f'The filename is still not valid. {filename}')
        if filename:
            self.output_filename = filename

    def get_size_from_length(self):
        if 'Content-Length' in self.response_headers:
            content_length = 'Content-Length'
        elif 'content-length' in self.response_headers:
            content_length = 'content-length'
        else:
            return -1
        return int(self.response_headers[content_length])

    def get_size_from_range(self):
        if 'Content-Range' in self.response_headers:
            content_range = 'Content-Range'
        elif 'content-range' in self.response_headers:
            content_range = 'content-range'
        else:
            return -1
        filesize = re.compile('^.*/([0-9]*)$').findall(self.response_headers[content_range])[0]
        return int(filesize)

    def get_redirect_url_from_response(self):
        '''
        For example,
        If current URL is: http://host1:port1/path/file001.txt
        Then, Location header could be:
        1) file002.txt -> http://host1:port1/path/file002.txt
        2) /file002.txt -> http://host1:port1/file002.txt
        3) //host2:port2/path2/file002.txt -> http://host2:port2/path2/file002.txt
        4) https://*** -> https://***
        '''
        redirect_url = self.get_location_from_response()
        if redirect_url is None:
            return None
        elif redirect_url.startswith('//'):
            return ''.join([self.get_scheme_str(self.scheme), redirect_url])
        elif redirect_url.startswith('/'):
            return '%s%s:%i%s' % \
                (
                    self.get_scheme_str(self.scheme),
                    self.host,
                    self.port,
                    redirect_url
                )
        elif redirect_url.find('://') < 0:
            return self.generate_url(redirect_url)
        else:
            return redirect_url

    def get_location_from_response(self):
        if 'location' in self.response_headers:
            return self.response_headers['location']
        elif 'Location' in self.response_headers['Location']:
            return self.response_headers['Location']
        else:
            return None
