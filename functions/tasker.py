#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .search import Search
from .connection import DownloadRecord

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
            download_records = [DownloadRecord()] * (self.config.search_amount + 1)
            self.search.makelist(download_records)
        else:
            pass
            
        # Do some parameter validation here.