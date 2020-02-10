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

    def makelist(self):
        current_time = time.time()
        self.connection = Connection(self.config, self.config.command_url)

