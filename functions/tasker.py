#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .search import Search
from .connection import Downloader

# python3 pyxel.py --search http://file.allitebooks.com/20200215/Serverless%20Programming%20Cookbook.pdf

class Tasker(object):
    def __init__(self, config):
        self.config = config
        self.search = Search(config)

    def start_task(self):
        print(f'Initializing download: {self.config.command_url}')
        if self.config.do_search:
            if self.config.verbose:
                print('Doing search...')
            downloaders = [Downloader()] * (self.config.search_amount + 1)
            self.search.makelist(downloaders)
        else:
            pass
            
        # Do some parameter validation here.