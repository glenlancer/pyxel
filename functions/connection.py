#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
# from urllib.parse import quote
from urllib.parse import urlparse
from .tcp import Tcp

'''
    Exclude the idea of: Ftp over Http proxy, only implement http over http proxy first.
'''

class DownloadRecord(object):
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

    TARGET_URL = 'target_url'
    HTTP_PROXY_URL = 'http_proxy_url'

    def __init__(self, ai_family, io_timeout, local_ifs=None):
        self.ai_family = ai_family
        self.io_timeout = io_timeout
        self.local_ifs = local_ifs
        self.output_filename = None
        self.request = None
        self.tcp = Tcp()
        self.status_code = 0
        self.target_scheme = None
        self.url_info = {}

    def is_connected(self):
        return self.tcp.is_connected()

    def set_url(self, new_url, url_type=TARGET_URL):
        parse_results = urlparse(new_url)
        self.target_scheme, port = self.parse_scheme(parse_results.scheme)
        user, password, hostname, new_port = self.parse_netloc(parse_results.netloc)
        file_dir, file = self.parse_path(parse_results.path)
        if new_port is not None:
            port = new_port
        self.url_info[url_type] = {
            'scheme': self.target_scheme,
            'port': port,
            'user': user,
            'password': password,
            'hostname': hostname,
            'file_dir': file_dir,
            'file': file,
            'cgi_params': parse_results.query
        }

    def parse_scheme(self, scheme):
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

    def parse_netloc(self, netloc):
        rest_of_netloc, user, password = self.parse_user_and_password(netloc)
        hostname, port = self.parse_hostname_and_port(rest_of_netloc)
        return user, password, hostname, port

    def parse_user_and_password(self, netloc):
        '''
            netloc example: username:password@www.my_site.com:123
        '''
        split_result = netloc.split('@')
        if len(split_result) < 2:
            if self.target_scheme == Connection.FTP:
                user = 'anonymous'
                password = 'anonymous'
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
        #file_dir, file = re.compile('^(.*/)([^/]*)$').findall(quote(path))[0]
        file_dir, file = re.compile('^(.*/)([^/]*)$').findall(path)[0]
        return file_dir, file

    def generate_original_url(self):
        url = Connection.get_scheme(self.scheme)
        if self.user != '' and self.password != '':
            url = ''.join([url_scheme, self.user, ':', self.password, '@'])
        return ''.join([url, self.hostname, ':', str(self.port), self.dir, self.file])

    def get_url_filename(self):
        return self.url_info[TARGET_URL]['file']

    def strip_cgi_parameters(self):
        self.url_info[TARGET_URL]['cgi_params'] = None

    @staticmethod
    def get_scheme(protocol):
        if protocol == Connection.FTP:
            return 'ftp://'
        elif protocol == Connection.FTPS:
            return 'ftps://'
        elif protocol == Connection.HTTP:
            return 'http://'
        elif protocol == Connection.HTTPS:
            return 'https://'

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
            raise Exception(f'Exception in {__name__}: unsupported scheme from {url}.')

    @staticmethod
    def is_secure_scheme(scheme):
        return (scheme == Connection.HTTPS) or (scheme == Connection.FTPS)
