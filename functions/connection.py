#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
from urllib.parse import quote
from urllib.parse import urlparse
from .ftp import Ftp
from .http import Http

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

    DEFAULT_PROTOCOL = HTTP
    DEFAULT_PORT = HTTP_DEFAULT_PORT

    def __init__(self, ai_family, io_timeout, http_proxy=None, no_proxies=None, local_if=None):
        self.ai_family = ai_family
        self.io_timeout = io_timeout
        self.http_proxy = http_proxy
        self.no_proxies = no_proxies
        self.local_if = local_if
        self.request = None
        self.check_http_proxy()

    def check_http_proxy(self):
        for no_proxy in self.config.no_proxies:
            if self.hostname == no_proxy:
                self.http_proxy = None
                break

    def parse_url(self, new_url):
        self.url = new_url
        parse_results = urlparse(self.url)
        self.parse_scheme(parse_results.scheme)
        self.parse_netloc(parse_results.netloc)
        self.parse_path(parse_results.path)

    def parse_scheme(self, scheme):
        if scheme.lower() == 'ftp':
            self.scheme = Connection.FTP
            self.port = Connection.FTP_DEFAULT_PORT
        elif scheme.lower() == 'ftps':
            self.scheme = Connection.FTPS
            self.port = Connection.FTPS_DEFAULT_PORT
        elif scheme.lower() == 'http':
            self.scheme = Connection.HTTP
            self.port = Connection.HTTP_DEFAULT_PORT
        elif scheme.lower() == 'https':
            self.scheme = Connection.HTTPS
            self.port = Connection.HTTPS_DEFAULT_PORT
        else:
            raise Exception(f'Exception in {__name__}: unsupported scheme, {scheme}.')

    def parse_netloc(self, netloc):
        rest_of_netloc = self.parse_user_and_password(netloc)
        self.parse_hostname_and_port(rest_of_netloc)

    def parse_user_and_password(self, netloc):
        '''
            netloc example: username:password@www.my_site.com:123
        '''
        split_result = netloc.split('@')
        if len(split_result) < 2:
            if self.scheme['protocol'] == Connection.PROTOCOL_FTP:
                self.user = 'anonymous'
                self.password = 'anonymous'
            else:
                self.user = ''
                self.password = ''
            return split_result[0]
        else:
            self.user, self.password = split_result[0].split(':')
            return split_result[1]

    def parse_hostname_and_port(self, rest_of_netloc):
        if rest_of_netloc.startswith('['):
            self.hostname, port = re.compile('^(\[.+\]):{0,1}([0-9]*)$').findall(rest_of_netloc)[0]
            if port != '':
                self.port = int(port)
        else:
            split_result = rest_of_netloc.split(':')
            if len(split_result) > 1:
                self.hostname = split_result[0]
                self.port = split_result[1]
            else:
                self.hostname = split_result

    def parse_path(self, path):
        self.dir, self.file = re.compile('^(.*/)([^/]*)$').findall(quote(path))[0]

    def generate_original_url(self):
        url = Connection.get_scheme(self.scheme)
        if self.user != '' and self.password != '':
            url = ''.join([url_scheme, self.user, ':', self.password, '@'])
        return ''.join([url, self.hostname, ':', str(self.port), self.dir, self.file])

    def is_http_default_port(self):
        return (
            self.scheme == Connection.HTTP and self.port == Connection.HTTP_PORT
        ) or (
            self.scheme == Connection.HTTPS and self.port == Connection.HTTPS_PORT
        )

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