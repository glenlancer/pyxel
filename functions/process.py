#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import threading
import json
from urllib.parse import unquote

# Read this..
# https://my.oschina.net/u/211101?tab=newest&catalogId=135429

from .connection import Connection
from .config import PYXEL_DEBUG

class Process(object):
    # 100 KB
    MIN_CHUNK_WORTH = 100 * 1024

    def __init__(self, config, url):
        self.config = config
        self.url = url
        self.messages = []
        self.output_filename = ''
        self.buffer_filename = ''
        self.output_fd = None
        self.file_size = 0
        self.bytes_done = 0
        self.conns = []
        self.delay_time = {
            'sec': 0, 'nsec': 0
        }
        self.tuning_params()

    def __del__(self):
        for message in self.messages:
            print('Dump all stored messages.')
            print(message)

    def prepare_connections(self, num_of_connections=1):
        if Connection.get_scheme_from_url(self.url) in (Connection.HTTP, Connection.HTTPS):
            # Reminder, pass in local_ifs
            self.conns = [Http(
                self.config.ai_family,
                self.config.io_timeout,
                self.config.max_redirect
                self.config.headers,
                self.config.http_proxy,
                self.config.no_proxies,
                self.config.interfaces[0]
            )] * num_of_connections
        else:
            self.conns = [Ftp(
                self.config.ai_family,
                self.config.io_timeout,
                self.config.max_redirect,
                self.config.interfaces[0]
            )] * num_of_connections

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

    def set_output_filename(self):
        self.output_filename = unquote(self.conns[0].get_url_filename())
        if self.output_filename == '':
            # This happens when we download index page.
            self.output_filename = self.config.default_filename

    def new_preparation(self, url):
        self.prepare_connections()
        self.conns[0].set_url(url):
        self.conns[0].strip_cgi_parameters()
        self.set_output_filename()

        if self.config.no_clobber and os.path.isfile(self.output_filename):
            if os.path.isfile(''.join([self.output_filename, '.st']))
                print(f'Incomplete download found for {self.output_filename}, \
                    ignoring no-clobber option.\n')
            else:
                print(f'File {self.output_filename} already exists, not retrieving.')
                return False

        while True:
            if not self.conns[0].get_resource_info():
                return False
            if self.conns[0].status_code != -1:
                break
            # FTP protocol can't be redirected back to HTTP.

        self.file_size = self.conns[0].file_size
        if self.config.verbose:
            if self.file_size != Connection.MAX_FILESIZE:
                self.add_message(f'File size: {self.file_size} bytes.')
            else:
                self.add_message('File size: unavailable.')

    # map axel_open()
    def open_local_files(self, urls):
        self.output_fd = None
        if self.config.verbose:
            self.add_message(f'Opening output file {self.output_filename}')
        self.buffer_filename = ''.join([self.output_filename, '.st'])
        # Check if server knows about RESTart and switch back to single connection
        # download if necessary.
        if not self.conns[0].resuming_supported:
            self.set_single_connection()
        elif self.restore_state():
            self.output_fd = self.open_file(self.output_filename, os.O_WRONLY)
            if self.output_fd is None:
                return False
        if self.output_fd is None:
            self.divide()
            self.output_fd = self.open_file(self.output_filename, os.O_CREAT | O_WRONLY)
            if self.output_fd is None:
                return False
            # Check whether the fs can handle seeks to past EOF areas.
            self.check_seek_past_eof()
        return True

    def open_file(self, filename, mode):
        try:
            fd = os.open(self.output_filename, os.O_CREAT | O_WRONLY, 0o666)
        except Exception as e:
            self.add_message('Error opening local file. {}'.format(e.args[-1])
            return None
        return fd

    def restore_state(self):
        state = self.load_state()
        if state:
            self.num_of_connections = int(state['num_of_connections'])
            self.bytes_done = int(state['bytes_done'])
            assert self.num_of_connections == len(state['connections'])
            self.prepare_connections(self.num_of_connections)
            for i in range(self.conns):
                self.conns[i].current_byte = state['connections'][i].current_byte
                self.conns[i].last_byte = state['connections'][i].last_byte
            return True
        return False

    def set_single_connection(self):
        self.add_message(
            'Server doen\'t support resuming, '
            'starting from scratch with one connection.'
        )
        self.config.num_of_connections = 1

    def divide(self):
        '''
        Divide the file and set locations for each connection.
        Set followings,
        num_of_connections, current_byte, last_byte
        '''
        # Optimize the number of connections in case the file is small.
        max_conns = max(1, self.file_size // self.MIN_CHUNK_WORTH)
        if max_conns < self.config.num_of_connections:
            self.config.num_of_connections = max_conns
        self.prepare_connections(self.num_of_connections)
        # Calculate each segment's size
        seg_len = self.file_size // self.config.num_of_connections
        if seg_len == 0:
            print('Too few bytes remaining, forcing a single connection\n')
            self.config.num_of_connections = 1
            seg_len = self.file_size
            self.conns = [self.conns[0]]
        for i in range(self.config.num_of_connections):
            self.conns[i].current_byte = seg_len * i
            self.conns[i].last_byte = seg_len * (i + 1)
        # Last connection downloads remaining bytes
        remaining_bytes = self.file_size % seg_len
        self.conns[-1].last_byte += remaining_bytes
        if PYXEL_DEBUG:
            for i in range(self.config.num_of_connections):
                print('Downloading {0}-{1} using conn. {2}'.format(
                    self.conns[i].current_byte,
                    self.conns[i].last_byte,
                    i
                ))

    def add_message(self, message):
        self.messages.append(message)

    def start(self):
        

    def close(self):
        pass

    def load_state(self):
        if os.path.exists(self.buffer_filename):
            with open(self.buffer_filename, 'r') as file_obj:
                return json.load(file_obj)
        return None

    def save_state(self):
        # No use for .st file if the server doesn't support resuming.
        if not self.conn[0].resuming_supported:
            return
        assert len(self.conns) == self.config.num_of_connections
        state = {
            'num_of_connections': self.config.num_of_connections,
            'bytes_done': self.bytes_done,
            'connections': []
        }
        for conn in self.conns:
            state['connections'].append(
                {
                    'current_byte': conn.current_byte,
                    'last_byte': conn.last_byte
                }
            )
        with open(self.buffer_filename, 'w') as file_obj:
            json.dump(state, file_obj)

    def print_messages(self):
        pass