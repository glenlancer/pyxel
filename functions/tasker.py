#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .search import Search

class Tasker(object):
    def __init__(self, config):
        self.config = config
        self.search = Search(config)

    def start_task(self):
        print(f'Initializing download: {self.config.command_url}')
        if self.config.do_search:
            if self.config.verbose:
                print('Doing search...')
            self.search.makelist()
        else:
            pass
            
        # Do some parameter validation here.