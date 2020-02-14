#!/usr/bin/python3
# -*- coding: utf-8 -*-

import base64
from .connection import Connection

class Http(Connection):
    def __init__(self, ai_family, io_timeout, local_if=None, http_proxy, no_proxies):
        super(Http, self).__init__(ai_family, io_timeout, local_if)
        self.http_proxy = http_proxy
        self.no_proxies = no_proxies
        self.http_basic_auth = None
        self.request = None

    def check_http_proxy(self):
        for no_proxy in self.no_proxies:
            if self.hostname == no_proxy:
                self.http_proxy = None
                break

    def init(self):
        self.check_http_proxy()
        if not self.connect():
            pass

    def connect(self):
        if self.http_proxy is not None:
            self.set_url(self.http_proxy)
        if not self.tcp.connect(
            self.conn.hostname,
            self.conn.port,
            self.conn.scheme['is_secure'],
            self.conn.ai_family,
            self.conn.io_timeout,
            None):
            return False
        if self.conn.user and self.conn.password:
            self.basic_auth_token()
        return True

    def disconnect(self):
        self.tcp.close()

    def basic_auth_token(self):
        self.http_basic_auth = base64.b64encode(
            f'{self.conn.user}:{self.conn.password}'
        ).strip()

    def get(self):
        self.request = None
        if self.http_proxy is None:
            self.add_header(f'GET {self.dir}{self.file} HTTP /1.0')
            if self.is_http_default_port():
                self.add_header(f'Host: {self.conn.host}')
            else:
                self.add_header(f'Host: {self.conn.host:{self.conn.port}')
        else:
            if self.conn.is_http_default_port():
                self.add_header(f'GET: {self.conn.generate_url_without_port()} HTTP/1.0')
            else:
                self.add_header(f'GET: {self.conn.generate_url_with_port()} HTTP/1.0')
        if self.basic_auth_token:
            self.add_header(f'Authorization: Basic {self.basic_auth_token}')
        self.add_header('Accept: */*')
        if self.conn.firstbyte > = 0:
            if self.conn.lastbyte:
                self.add_header(f'Range: bytes={self.conn.firstbyte}-{self.conn.lastbyte}')
            else:
                self.add_header(f'Range: bytes={self.conn.firstbyte}-')

    def add_header(self, new_header):
        self.request = ''.join([self.request, new_header, '\r\n'])