#!/usr/bin/python3
# -*- coding: utf-8 -*-

import base64

class Http(object):
    def __init__(self, connection):
        self.connection = connection
        self.tcp = Tcp()
        self.http_basic_auth = False
        self.request = None

    def connect(self):
        if self.connection.proxy is not None:
            self.connection.parse_url(self.connection.proxy)
        if not self.tcp.connect(
            self.connection.hostname,
            self.connection.port,
            self.connection.scheme['is_secure'],
            self.connection.ai_family,
            self.connection.io_timeout,
            None
        ):
            return False
        if self.connection.user and self.connection.password:
            self.basic_auth_token()
        return True

    def disconnect(self):
        self.tcp.close()

    def basic_auth_token(self):
        self.http_basic_auth = base64.b64encode(
            f'{self.connection.user}:{self.connection.password}'
        ).strip()

    def get(self, url):
        self

    def add_header(self, new_header):
        self.request = ''.join([self.request, new_header])