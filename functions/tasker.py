#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .search import Search
from .connection import DownloadRecord

class Tasker(object):
    def __init__(self, config):
        self.config = config
        self.search = Search(config)

    def start_task(self):
        print(f'Initializing download: {self.config.command_url}')
        if self.config.do_search:
            if self.config.verbose:
                print('Doing search...')
            download_records = [DownloadRecord] * (self.config.search_amount + 1)
            self.search.makelist(download_records)
        else:
            pass
            
        # Do some parameter validation here.