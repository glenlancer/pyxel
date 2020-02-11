#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
from .connection import Connection

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
        self.connection = Connection(self.config, self.url)
        if not self.connection.setup():
            return False

if __name__ == '__main__':
    # Testing
    pass

