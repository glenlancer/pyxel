#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from urllib.parse import unquote

from .connection import Connection

class Process(object):
    def __init__(self, config):
        self.config = config
        self.url = self.config.command_url
        self.messages = []
        self.output_filename = ''
        self.buffer_filename = ''
        self.conns = []
        self.delay_time = {
            'sec': 0, 'nsec': 0
        }
        self.tuning_params()

    def prepare_connections(self):
        if Connection.get_scheme_from_url(self.url) in (Connection.HTTP, Connection.HTTPS):
            self.conns = [Http(
                self.config.ai_family,
                self.config.io_timeout,
                self.config.headers,
                self.config.http_proxy,
                self.config.no_proxies,
            )] * self.config.num_connections
        else:
            pass

    def tuning_params(self):
        if self.config.max_speed > 0:
            if self.config.max_speed * 16 // self.config.buffer_size < 8:
                if self.config.verbose:
                    self.add_message('Buffer resized for this speed.')
                self.config.buffer_size = self.config.max_speed
            delay = 1000000000 * \
                self.config.buffer_size * \
                self.config.num_connections / \
                self.config.max_speed
            self.delay_time['sec'] = delay // 1000000000
            self.delay_time['nsec'] = delay % 1000000000

    def new_process(self):
        self.prepare_connections()
        self.conns[0].set_url(url, Connection.TARGET_URL)
        # Setting local_if here?
        self.conns[0].strip_cgi_parameters()
        self.output_filename = unquote(self.conns[0].get_url_filename())
        if self.output_filename == '':
            self.output_filename = self.config.default_filename
        if self.config.no_clobber and os.path.isfile(self.output_filename):
            if os.path.isfile(''.join([self.output_filename, '.st']))
                print(f'Incomplete download found for {self.output_filename}, \
                    ignoring no-clobber option.\n')
            else:
                print(f'File {self.output_filename} already exists, not retrieving.')
                return False
        


    def new_process(self, download_records):
        pass

    def open_process(self, urls):
        if self.config.verbose:

    def add_message(self, message):
        self.messages.append(message)