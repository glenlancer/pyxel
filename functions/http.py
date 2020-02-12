#!/usr/bin/python3
# -*- coding: utf-8 -*-

import base64

class Http(object):
    def __init__(self, conn):
        self.conn = conn
        self.tcp = Tcp()
        self.http_basic_auth = None
        self.request = None

    def connect(self):
        if self.conn.proxy is not None:
            self.conn.parse_url(self.conn.proxy)
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
        if self.conn.proxy is None:
            self.add_header(f'GET {self.conn.dir}{self.conn.file} HTTP /1.0')
            if self.conn.is_http_default_port():
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