#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
from urllib.parse import urlparse
from .tcp import Tcp

from .config import PYXEL_DEBUG

class Downloader(object):
    def __init__(self, url=None):
        self.url = url
        self.speed_start_time = 0
        self.speed = 0
        self.size = 0
        self.speed_thread = None

class Connection(object):
    FTP_DEFAULT_PORT = 21
    FTPS_DEFAULT_PORT = 990
    HTTP_DEFAULT_PORT = 80
    HTTPS_DEFAULT_PORT = 443

    HTTP = 0
    HTTPS = 1
    FTP = 2
    FTPS = 3

    ANONYMOUS_USER = 'anonymous'
    ANONYMOUS_PASS = 'mailto:anonymous@pyxel.project'

    def __init__(self, ai_family, io_timeout, local_ifs=None):
        self.ai_family = ai_family
        self.io_timeout = io_timeout
        self.local_ifs = local_ifs
        self.output_filename = None
        self.request = None
        self.tcp = Tcp()
        self.status_code = None
        self.file_size = None
        self.init_url_params()

    def is_connected(self):
        return self.tcp.is_connected()

    def init_url_params(self):
        self.url = None
        self.scheme = None
        self.port = None
        self.user = None
        self.password = None
        self.host = None
        self.dir = None
        self.file_size = None
        self.cgi_params = None

    def set_url(self, url):
        self.init_url_params()
        self.url = url
        parse_results = urlparse(self.url)
        self.scheme, self.port = self.parse_scheme(parse_results.scheme)
        self.user, self.password, self.host, new_port = self.parse_netloc(parse_results.netloc)
        self.dir, self.file = self.parse_path(parse_results.path)
        if new_port is not None:
            self.port = new_port
        self.cgi_params = 
        if PYXEL_DEBUG:
            sys.stderr.write('--- URL Parsing ---\n')
            sys.stderr.write(f'Url: {self.url}')
            sys.stderr.write('Pasring results:\n')
            sys.stderr.write(f'Scheme: {self.scheme}')
            sys.stderr.write(f'Port: {self.port}')
            sys.stderr.write(f'User: {self.user}')
            sys.stderr.write(f'Password: {self.password}')
            sys.stderr.write(f'Host: {self.host}')
            sys.stderr.write(f'Dir: {self.dir}')
            sys.stderr.write(f'File: {self.file}')
            sys.stderr.write(f'Cgi: {self.cgi_params}')
            sys.stderr.write('--- End of Url Parsing ---\n')

    def parse_scheme(self, scheme):
        if scheme.lower() == 'ftp':
            return self.FTP, self.FTP_DEFAULT_PORT
        elif scheme.lower() == 'ftps':
            return self.FTPS, self.FTPS_DEFAULT_PORT
        elif scheme.lower() == 'http':
            return self.HTTP, self.HTTP_DEFAULT_PORT
        elif scheme.lower() == 'https':
            return self.HTTPS, self.HTTPS_DEFAULT_PORT
        else:
            raise Exception(f'Exception in {__name__}: unsupported scheme, {scheme}.')

    def parse_netloc(self, netloc):
        rest_of_netloc, user, password = self.parse_user_and_password(netloc)
        hostname, port = self.parse_hostname_and_port(rest_of_netloc)
        return user, password, hostname, port

    def parse_user_and_password(self, netloc):
        '''
            netloc example: 
            (1) username:password@www.my_site.com:123
            (2) www.my_site.com:123
        '''
        split_result = netloc.split('@')
        if len(split_result) < 2:
            if self.scheme in (self.FTP, self.FTPS):
                user = self.ANONYMOUS_USER
                password = self.ANONYMOUS_PASS
            else:
                user = ''
                password = ''
            return split_result[0], user, password
        else:
            user, password = split_result[0].split(':')
            return split_result[1], user, password

    def parse_hostname_and_port(self, rest_of_netloc):
        if rest_of_netloc.startswith('['):
            hostname, port = re.compile('^(\[.+\]):{0,1}([0-9]*)$').findall(rest_of_netloc)[0]
            if port != '':
                port = int(port)
        else:
            split_result = rest_of_netloc.split(':')
            if len(split_result) > 1:
                hostname = split_result[0]
                port = split_result[1]
            else:
                hostname = split_result[0]
                port = None
        return hostname, port

    def parse_path(self, path):
        return re.compile('^(.*/)([^/]*)$').findall(path)[0]

    def generate_url(self, with_cgi_params=False):
        full_url = self.get_scheme(self.scheme)
        if self.user and self.user != 'anonymous':
            full_url = ''.join([
                full_url, self.user, ':', self.password, '@'
            ])
        full_url = ''.join([
            full_url, self.host, ':', self.port, self.dir, self.file
        ])
        if with_cgi_params:
            full_url = ''.join([full_url, '?', self.cgi_params])
        return full_url

    @staticmethod
    def get_scheme(protocol):
        if protocol == self.FTP:
            return 'ftp://'
        elif protocol == self.FTPS:
            return 'ftps://'
        elif protocol == self.HTTP:
            return 'http://'
        elif protocol == self.HTTPS:
            return 'https://'

    @staticmethod
    def get_scheme_from_url(url):
        if url.lower().startswith('https://'):
            return self.HTTPS
        elif url.lower().startswith('http://'):
            return self.HTTP
        elif url.lower().startswith('ftps://'):
            return self.FTPS
        elif url.lower().startswith('ftp://'):
            return self.FTP
        else:
            raise Exception(f'Exception in {__name__}: unsupported scheme from {url}.')

    @staticmethod
    def is_secure_scheme(scheme):
        return (scheme == self.HTTPS) or (scheme == self.FTPS)
