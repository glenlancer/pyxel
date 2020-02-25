#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import signal

from .search import Search
from .process import Process

# python3 pyxel.py --search=2 http://file.allitebooks.com/20200215/Serverless%20Programming%20Cookbook.pdf

class Tasker(object):
    def __init__(self, config, url):
        self.config = config
        self.url = url
        self.search = Search(config, url)
        self.process = Process(config)
        self.run = False

    def start_task(self):
        print(f'Initializing download: {self.url}')
        if self.config.do_search:
            # Do nothing..
            print('do_search is not supported yet.')
        if not self.process.new_preparation(url):
            self.process.print_messages()
            return False
        if self.config.output_direction:
            if not self.use_output_direction():
                return False
        else:
            self.check_local_files()
        self.setup_signal_hook()

    def use_output_direction(self):
        output_filename = self.config.output_direction
        if os.path.isdir(output_filename):
            output_filename = ''.join([
                output_filename,
                '/',
                self.process.output_filename
            ])
        state_filename = ''.join([
            output_filename,
            '.st'
        ])
        if os.path.exists(output_filename) and not os.path.exists(state_filename):
            sys.stderr.write('No state file, cannot resume!\n')
            return False
        if os.path.exists(state_filename) and not os.path.exists(output_filename):
            sys.stderr.write('State file found, but no downloaded data. Starting from scratch.\n')
            os.unlink(state_filename)
        self.process.output_filename = output_filename
        return True

    def check_local_files(self):
        i = 0
        output_filename = self.process.output_filename
        length = len(output_filename)
        while True:
            state_filename = ''.join([
                output_filename,
                '.st'
            ])
            f_exists = os.path.exists(output_filename)
            st_exists = os.path.exists(state_filename)
            if f_exists:
                if self.process.conn[0].supported and st_exists:
                    break
            elif not st_exists:
                break
            if len(output_filename) == length:
                output_filename = ''.join([
                    output_filename,
                    '.{0}'.format(i)
                ])
            else:
                output_filename = ''.join([
                    output_filename[:-(i // 10 + 1)],
                    '.{}'.format(i)
                ])
        self.process.output_filename = output_filename

    def setup_signal_hook(self):
        signal.singal(signal.SIGINT, self.stop)
        signal.signal(singal.SIGTERM, self.stop)
    
    def stop(self):
        self.run = False