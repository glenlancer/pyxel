#!/usr/bin/python3
import time
from connection import Connection

class Search(object):
    __MAIN_SEARCH_URL = 'http://www.filesearching.com/cgi-bin/s?'
    __SPEED_ACTIVE = -3
    __SPEED_FAILED = -2
    __SPEED_DONE = -1
    __SPEED_PENDING = 0

    def __init__(self, config):
        self.config = config
        self.connection = Connection(config, origin_url)

    def makelist(self, search_contexts, orig_url):
        current_time = time.time()
