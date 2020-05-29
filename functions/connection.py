#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import threading
from urllib.parse import urlparse

from .tcp import Tcp
from .config import PYXEL_DEBUG

class Connection(object):
    '''
    A Connection might be a Http or Ftp connection
    '''
    HTTP = 0
    HTTPS = 1
    FTP = 2
    FTPS = 3

    FTP_DEFAULT_PORT = 21
    FTPS_DEFAULT_PORT = 990
    HTTP_DEFAULT_PORT = 80
    HTTPS_DEFAULT_PORT = 443

    ANONYMOUS_USER = 'anonymous'
    ANONYMOUS_PASS = 'mailto:anonymous@unkonwn.com'

    MAX_FILESIZE = sys.maxsize

    def __init__(self, ai_family, io_timeout, max_redirect, local_ifs=[]):
        self.ai_family = ai_family
        self.io_timeout = io_timeout
        self.max_redirect = max_redirect

        # A list of local interface names
        self.local_ifs = local_ifs
        # Store the generated request message as a string
        self.request = None
        # Http status code
        self.status_code = None
        # Store the file name derived from response message
        self.output_filename = None
        # The tcp tunnel used by application layer
        self.tcp = Tcp()

        # Define and initialize all parts that constitute an URL 
        self.init_url_params()

        # Store the file size derived from response message
        self.file_size = None
        self.first_byte = None
        self.current_byte = None
        self.last_byte = None
        self.last_transfer = None
        self.lock = threading.Lock()

        # When a connection is enabled, it means all data read from socket shall be written
        # into the file
        self.enabled = False
        # When a connection thread is about to run till it finishes its job, in_progress is True
        self.in_progress = False

        # Store the thread reference when multi-threading
        self.setup_thread = None
        self.message = None

        # If a Http is redirected to Ftp, set this flag
        self.redirect_to_ftp = False

    def init_url_params(self):
        ''' 
        Store the url and variables parsed from it
        URL example:
        http://www.example.com:80/path/to/myfile.html?key1=value1&key2=value2#SomewhereInTheDocument
        Protocol: http
        Domain name: www.example.com
        Port: 80
        Path to the file: /path/to/myfile.html
        Parameters: ?Key1=value1&key2=value2
        Anchor: #SomewhereInTheDocument
        '''
        self.url = None
        self.scheme = None
        self.port = None
        self.user = None
        self.password = None
        self.host = None
        self.filedir = None
        self.filename = None
        self.cgi_params = None

    def is_connected(self):
        return self.tcp.is_connected()

    def get_socket_fd(self):
        return self.tcp.socket_fd

    def recv_data(self, msg_size):
        '''
        Receive binary data from Tcp connection
        In Http, it's the binary data attached after Http response header
        '''
        try:
            return self.tcp.recv(msg_size)
        except Exception as e:
            sys.stderr.write(f'Exception in {__name__}: {e.args[-1]}\n')
            return b''

    def is_secure_scheme(self):
        return (self.scheme == self.HTTPS) or (self.scheme == self.FTPS)

    def set_url(self, url):
        '''
        Set Url to the connection and have it parsed.
        '''
        self.url = url
        self.scheme, self.port, self.user, self.password, \
        self.host, self.filedir, self.filename, self.cgi_params \
            = self.analyse_url(url)

    def generate_url(self, with_cgi_params=False):
        full_url = self.get_scheme_str(self.scheme)
        if self.user and self.user != 'anonymous':
            full_url = ''.join([full_url, self.user, ':', self.password, '@'])
        full_url = ''.join([full_url, self.host, ':', str(self.port), self.filedir, self.filename ])
        if with_cgi_params:
            full_url = ''.join([full_url, '?', self.cgi_params])
        return full_url

    @staticmethod
    def analyse_url(url):
        parse_results = urlparse(url)
        scheme, port = Connection.parse_scheme(parse_results.scheme)
        user, password, host, new_port = Connection.parse_netloc(scheme, parse_results.netloc)
        filedir, filename = Connection.parse_path(parse_results.path)
        if new_port is not None:
            port = new_port
        cgi_params = parse_results.query
        if PYXEL_DEBUG:
            sys.stderr.write('--- URL Parsing ---\n')
            sys.stderr.write(f'Url: {url}\n')
            sys.stderr.write('Pasring results:\n')
            sys.stderr.write(f'Scheme: {Connection.get_scheme_str(scheme)[:-3]}\n')
            sys.stderr.write(f'Port: {port}\n')
            sys.stderr.write(f'User: {user}\n')
            sys.stderr.write(f'Password: {password}\n')
            sys.stderr.write(f'Host: {host}\n')
            sys.stderr.write(f'Dir: {filedir}\n')
            sys.stderr.write(f'File: {filename}\n')
            sys.stderr.write(f'Cgi: {cgi_params}\n')
            sys.stderr.write('--- End of Url Parsing ---\n')
        return scheme, port, user, password, host, filedir, filename, cgi_params

    @staticmethod
    def parse_scheme(scheme):
        if scheme.lower() == 'ftp':
            return Connection.FTP, Connection.FTP_DEFAULT_PORT
        elif scheme.lower() == 'ftps':
            return Connection.FTPS, Connection.FTPS_DEFAULT_PORT
        elif scheme.lower() == 'http':
            return Connection.HTTP, Connection.HTTP_DEFAULT_PORT
        elif scheme.lower() == 'https':
            return Connection.HTTPS, Connection.HTTPS_DEFAULT_PORT
        else:
            raise Exception(f'Exception in {__name__}: unsupported scheme, {scheme}.')

    @staticmethod
    def parse_path(path):
        return re.compile('^(.*/)([^/]*)$').findall(path)[0]

    @staticmethod
    def parse_netloc(scheme, netloc):
        rest_of_netloc, user, password = Connection.parse_user_and_password(scheme, netloc)
        hostname, port = Connection.parse_hostname_and_port(rest_of_netloc)
        return user, password, hostname, port

    @staticmethod
    def parse_user_and_password(scheme, netloc):
        '''
            netloc example: 
            (1) username:password@www.my_site.com:123
            (2) www.my_site.com:123
        '''
        split_result = netloc.split('@')
        if len(split_result) < 2:
            if scheme in (Connection.FTP, Connection.FTPS):
                user, password = Connection.ANONYMOUS_USER, Connection.ANONYMOUS_PASS
            else:
                user, password = '', ''
            return split_result[0], user, password
        else:
            user, password = split_result[0].split(':')
            return split_result[1], user, password

    @staticmethod
    def parse_hostname_and_port(rest_of_netloc):
        if rest_of_netloc.startswith('['):
            hostname, port = re.compile('^(\[.+\]):{0,1}([0-9]*)$').findall(rest_of_netloc)[0]
            if port != '':
                port = int(port)
        else:
            split_result = rest_of_netloc.split(':')
            if len(split_result) > 1:
                hostname = split_result[0]
                port = int(split_result[1])
            else:
                hostname = split_result[0]
                port = None
        return hostname, port

    @staticmethod
    def get_scheme_str(scheme):
        if scheme == Connection.FTP:
            return 'ftp://'
        elif scheme == Connection.FTPS:
            return 'ftps://'
        elif scheme == Connection.HTTP:
            return 'http://'
        elif scheme == Connection.HTTPS:
            return 'https://'
        else:
            raise Exception(f'Exception in {__name__}: unsupported scheme as {scheme}')

    @staticmethod
    def get_scheme_from_url(url):
        if url.lower().startswith('https://'):
            return Connection.HTTPS
        elif url.lower().startswith('http://'):
            return Connection.HTTP
        elif url.lower().startswith('ftps://'):
            return Connection.FTPS
        elif url.lower().startswith('ftp://'):
            return Connection.FTP
        else:
            raise Exception(f'Exception in {__name__}: unsupported scheme from {url}')
