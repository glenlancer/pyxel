#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .search import Search
from .process import Process

# python3 pyxel.py --search=2 http://file.allitebooks.com/20200215/Serverless%20Programming%20Cookbook.pdf

class Tasker(object):
    def __init__(self, config, url):
        self.config = config
        self.url = url
        self.search = Search(config, url)
        self.process = Process(config, url)

    def start_task(self):
        print(f'Initializing download: {self.url}')
        if self.config.do_search:
            # Do nothing..
            print('do_search is not supported yet.')
        if not self.process.new_preparation(url):
            self.process.print_messages()
            return False
        
        