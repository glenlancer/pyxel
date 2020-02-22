#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
from .connection import Connection
from .http import Http
from .ftp import Ftp

'''
    The filesearching function seems very poor, just make stubs for it.
'''

class Search(object):
    __MAIN_SEARCH_URL = 'http://www.filesearching.com/cgi-bin/s?'
    __SPEED_ACTIVE = -3
    __SPEED_FAILED = -2
    __SPEED_DONE = -1
    __SPEED_PENDING = 0

    def __init__(self, config, url):
        self.config = config
        self.url = url

    def makelist(self, downloaders):
        beginning_time = time.time()
        if Connection.get_scheme_from_url(self.url) in (Connection.HTTP, Connection.HTTPS):
            self.conn = Http(
                self.config.ai_family,
                self.config.io_timeout,
                self.config.max_redirect,
                self.config.headers,
                self.config.http_proxy,
                self.config.no_proxies,
            )
        else:
            # Else it's a ftp connection.
            pass
        if False in (self.conn.set_url(self.url), self.conn.get_resource_info()):
            return False
        downloaders[0].url = self.url
        downloaders[0].speed = int(1 + 1000 * (time.time() - beginning_time))
        downloaders[0].file_size = self.conn.file_size
        file_search_url = ''.join([
            self.__MAIN_SEARCH_URL,
            'w=a&',      # TODO describe
            'x=15&y=15&' # TODO describe
            's=on&',     # Size in bytes
            'e=on&',     # Exact search
            'l=en&',     # Language
            't=f&',      # Search Type
            'o=n&',      # Sorting
            f'q={self.conn.file}&',            # Filename
            f'm={self.config.search_amount}&', # Num. of results
            f's1={self.conn.file_size}&s2={self.conn.file_size}' # Size (min/max)
        ])

if __name__ == '__main__':
    # Testing
    pass

