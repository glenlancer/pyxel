#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import struct
import threading
from urllib.parse import unquote

from .connection import Connection

class Process(object):
    # 100 KB
    MIN_CHUNK_WORTH = 100 * 1024

    def __init__(self, config):
        self.config = config
        self.url = self.config.command_url
        self.messages = []
        self.output_filename = ''
        self.buffer_filename = ''
        self.file_size = 0
        self.bytes_done = 0
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
                self.config.max_redirect
                self.config.headers,
                self.config.http_proxy,
                self.config.no_proxies,
            )] * self.config.num_of_connections
        else:
            pass
        for conn in self.conns:
            conn.lock = threading.Lock()

    def tuning_params(self):
        if self.config.max_speed > 0:
            if self.config.max_speed * 16 // self.config.buffer_size < 8:
                if self.config.verbose:
                    self.add_message('Buffer resized for this speed.')
                self.config.buffer_size = self.config.max_speed
            delay = 1000000000 * \
                self.config.buffer_size * \
                self.config.num_of_connections / \
                self.config.max_speed
            self.delay_time['sec'] = delay // 1000000000
            self.delay_time['nsec'] = delay % 1000000000

    def new_preparation(self, url):
        self.prepare_connections()
        self.conns[0].set_url(url)
        # Setting local_if here?
        self.conns[0].strip_cgi_parameters()
        self.output_filename = unquote(self.conns[0].get_url_filename())
        if self.output_filename == '':
            # This happens when we download index page.
            self.output_filename = self.config.default_filename
        if self.config.no_clobber and os.path.isfile(self.output_filename):
            if os.path.isfile(''.join([self.output_filename, '.st']))
                print(f'Incomplete download found for {self.output_filename}, \
                    ignoring no-clobber option.\n')
            else:
                print(f'File {self.output_filename} already exists, not retrieving.')
                return False
        # 
        if not self.conns[0].get_resource_info():
            return False
        if self.config.verbose:
            print('')

    def divide(self):
        '''
        Divide the file and set locations for each connection.
        '''
        # Optimize the number of connections in case the file is small.
        max_conns = max(1, self.file_size // self.MIN_CHUNK_WORTH)
        if max_conns < self.config.num_of_connections:
            self.config.num_of_connections = max_conns
        # Calculate each segment's size
        seg_len = self.file_size // self.config.num_of_connections
        if seg_len == 0:
            print('Too few bytes remaining, forcing a single connection\n')
            self.config.num_of_connections = 1
            seg_len = self.file_size

    def open_process(self, urls):
        if self.config.verbose:

    def add_message(self, message):
        self.messages.append(message)

    def close(self):
        pass

    def save_state(self):
        # No use for .st file if the server doesn't support resuming.
        if not self.conn[0].resuming_supported:
            return
        state_filename = ''.join([self.output_filename, '.st'])
        try:
            fd = os.open(
                state_filename,
                os.O_CREAT | os.O_TRUNC | os.O_WRONLY,
                0o666)
        except Exception as e:
            sys.stderr.write(f'Can\'t open file {state_filename}: {e.message}\n')
            return
        num_of_connections = struct.pack('I', self.config.num_of_connections)
        nwrite = os.write(fd, num_of_connections)
        assert(nwrite == len(num_of_connections)
        bytes_done = struct.pack('I', self.bytes_done)
        nwrite = os.write(fd, bytes_done)
        assert(nwrite == len(bytes_done))
        for conn in self.conns:
            current_byte = struct.pack('I', conn.current_byte)
            nwrite = os.write(fd, current_byte)
            assert(nwrite == len(current_byte))
            last_byte = struct.pack('I', conn.last_byte)
            nwrite = os.write(fd, last_byte)
            assert(nwrite == len(last_byte))
        os.close(fd)
