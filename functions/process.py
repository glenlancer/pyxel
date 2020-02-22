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

    def __init__(self, config, url):
        self.config = config
        self.url = url
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

    def __del__(self):
        for message in self.messages:
            print('Dump all stored messages.')
            print(message)

    def prepare_connections(self):
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
            )]
        else:
            self.conns = [Ftp(
                self.config.ai_family,
                self.config.io_timeout,
                self.config.max_redirect,
                self.config.interfaces[0]
            )]
        conn[0].lock = threading.Lock()

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

    def open_process(self, urls):
        if self.config.verbose:
            self.add_message(f'Opening output file {self.output_filename}')
        self.buffer_filename = ''.join([self.output_filename, '.st'])

        # Check if server knows about RESTart and switch back to single connection
        # download if necessary.
        fd = None
        if not self.conns[0].resuming_supported:
            self.add_message(
                'Server doen\'t support resuming, '
                'starting from scratch with one connection.'
            )
            self.config.num_of_connections = 1
            self.divide()
        else:
            fd = self.load_state()

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

    def add_message(self, message):
        self.messages.append(message)

    def start(self):
        

    def close(self):
        pass

    def load_state(self):
        try:
            fd = os.open(self.buffer_filename, os.O_RDONLY)
            file_size = os.lseek(fd, 0, os.SEEK_END)
            os.lseek(fd, 0, os.SEEK_SET)
            read_in_bytes = os.read(fd, struct.calcsize('I'))
            if len(read_in_bytes) != struct.calcsize('I'):
                print(f'{self.buffer_filename}: Error, truncated state file.')
                os.close(fd)
                return 0
            self.config.num_of_connections = read_in_bytes.decode()
            if self.config.num_of_connections < 1:
                print('Bogus number of connections stored in state file.')
                os.close(fd)
                return 0
        except Exception as e:
            sys.stderr.write(f'Can\'t load file {self.buffer_filename}: {e.message}\n')
            return -1
       

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

    def print_messages(self):
        pass