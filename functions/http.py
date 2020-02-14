#!/usr/bin/python3
# -*- coding: utf-8 -*-

import base64
from .connection import Connection

class Http(Connection):
    def __init__(self, ai_family, io_timeout, headers={}, local_if=None, http_proxy=None, no_proxies=None):
        super(Http, self).__init__(ai_family, io_timeout, local_if)
        self.headers = headers
        self.http_proxy = http_proxy
        self.no_proxies = no_proxies
        self.http_basic_auth = None
        self.request = None

    def check_http_proxy(self):
        for no_proxy in self.no_proxies:
            if self.hostname == no_proxy:
                self.http_proxy = None
                break

    def init(self, url):
        self.set_url(url, Connection.TARGET_URL)
        self.check_http_proxy()
        if not self.connect():
            self.disconnect()
            return False
        return True

    def setup(self):
        self.first_byte = -1
        if self.supported:
            self.first_byte = self.current_byte
        self.http_basic_get()
        self.http_additional_headers()

    def exec(self):
        pass

    def connect(self):
        url_type = Connection.TARGET_URL
        if self.http_proxy is not None:
            self.set_url(self.http_proxy, Connection.HTTP_PROXY_URL)
            url_type = Connection.HTTP_PROXY_URL
        if not self.tcp.connect(
            self.url_info[url_type]['hostname'],
            self.url_info[url_type]['port']
            self.is_secure_scheme(self.url_info[url_type]['scheme']),
            self.ai_family,
            self.io_timeout,
            self.local_if):
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
        self.request = None
        info = self.url_info[Connection.TARGET_URL]
        if self.http_proxy is None:
            self.add_header(f'GET {info['file_dir']}{info['file']} HTTP /1.0')
            if self.is_default_port(info['scheme'], info['port']):
                self.add_header(f'Host: {info['hostname']}')
            else:
                self.add_header(f'Host: {info['hostname']:{info['port']}')
        else:
            proto_str = Connection.get_scheme(info['scheme'])
            if self.is_default_port(info['port']):
                get_str = f'{proto_str}{info['hostname']}{info['file_dir']}{info['file']}'
            else:
                get_str = f'{proto_str}{info['hostname']}:{info['port']}{info['file_dir']}{info['file']}'
            self.add_header(f'GET {get_str} HTTP/1.0')
        if self.basic_auth_token:
            self.add_header(f'Authorization: Basic {self.basic_auth_token}')
        self.add_header('Accept: */*')
        if self.firstbyte >= 0:
            if self.lastbyte:
                self.add_header(f'Range: bytes={self.firstbyte}-{self.lastbyte}')
            else:
                self.add_header(f'Range: bytes={self.firstbyte}-')

    def http_additional_headers(self):
        for key, value in self.headers.items:
            self.add_header(f'{key}: {value}')

    def add_header(self, new_header):
        self.request = ''.join([self.request, new_header, '\r\n'])

    def is_default_port(self, port):
        return (
            port == Connection.HTTP_DEFAULT_PORT
        ) or (
            port == Connection.HTTPS_DEFAULT_PORT
        )