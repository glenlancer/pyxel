#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
from .connection import Connection
from .http import Http
from .ftp import Ftp

class Search(object):
    __MAIN_SEARCH_URL = 'http://www.filesearching.com/cgi-bin/s?'
    __SPEED_ACTIVE = -3
    __SPEED_FAILED = -2
    __SPEED_DONE = -1
    __SPEED_PENDING = 0

    def __init__(self, config):
        self.config = config
        self.url = self.config.command_url

    def makelist(self, download_records):
        current_time = time.time()
        if Connection.get_scheme_from_url(self.url) in (Connection.HTTP, Connection.HTTPS):
            self.conn = Http(
                self.config.ai_family,
                self.config.io_timeout,
                self.config.headers,
                self.config.http_proxy,
                self.config.no_proxies,
            )
        else:
            # Else it's a ftp connection.
            pass
        if False in (self.conn.init(self.url), self.conn.get_info()):
            return False

if __name__ == '__main__':
    # Testing
    pass

