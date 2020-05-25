#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import threading
import json
import time
import ctypes
from urllib.parse import unquote

# Read this..
# https://my.oschina.net/u/211101?tab=newest&catalogId=135429

from .connection import Connection
from .http import Http
from .ftp import Ftp
from .config import PYXEL_DEBUG

class Process(object):
    # 100 KB
    MIN_CHUNK_WORTH = 100 * 1024

    # 1 sec == 1000000000 nsec
    SMALLEST_DELAY_IN_SEC = 0.0001
    NSECs_IN_1_SEC = 1000000000
    NSECs_Increment = 10000000
    DELAY_ADJUST_PERCENT = 0.05

    def __init__(self, config):
        self.config = config
        self.url = None

        # File related info
        self.output_fd = None
        self.output_filename = None
        self.state_filename = None
        self.file_size = 0
        self.bytes_done = 0
        self.bytes_per_second = 0
        self.start_byte = 0

        self.start_time = None
        self.finish_time = None

        self.delay_time_for_process = {
            'sec': 0, 'nsec': 0
        }
        self.delay_time_for_waiting_connection = {
            'sec': 0, 'nsec': Process.NSECs_IN_1_SEC // 10
        }
        self.next_state = 0
        self.ready = False

        # Store the connection objects, each works on a portion of the data to be downloaded
        self.conns = []

        # A list of messages record what happened in Process()
        self.messages = []

    def __del__(self):
        if self.messages:
            sys.stdout.write(f'Dump all stored messages for {__name__}\n')
            self.process_print_messages()

    def process_print_messages(self):
        for message in self.messages:
            sys.stdout.write(''.join([message, '\n']))
        self.messages = []

    def prepare_connections(self, num_of_connections):
        for _ in range(num_of_connections):
            if Connection.get_scheme_from_url(self.url) in (Connection.HTTP, Connection.HTTPS):
                new_conn = Http(
                    self.config.ai_family,
                    self.config.io_timeout,
                    self.config.max_redirect,
                    self.config.headers,
                    self.config.http_proxy,
                    self.config.no_proxies,
                    self.config.interfaces[0]
                )
            else:
                new_conn = Ftp(
                    self.config.ai_family,
                    self.config.io_timeout,
                    self.config.max_redirect,
                    self.config.interfaces[0]
                )
            self.conns.append(new_conn)

    def prepare_1st_connection(self):
        self.conns = []
        self.prepare_connections(1)

    def prepare_other_connections(self):
        assert len(self.conns) == 1
        self.prepare_connections(self.config.num_of_connections - 1)

    def is_resuming_supported(self):
        return self.conns[0].resuming_supported

    def tuning_params(self):
        '''
        If config.max_speed is defined, then adjust config.buffer_size and delay_time_for_process
        '''
        if self.config.max_speed > 0:
            # To make max_speed / buffer_size < 0.5
            if self.config.max_speed * 16 // self.config.buffer_size < 8:
                if self.config.verbose:
                    self.add_message(
                        'Buffer resized for this speed. '
                        f'{self.config.buffer_size} to {self.config.max_speed}'
                    )
                self.config.buffer_size = self.config.max_speed
            delay = Process.NSECs_IN_1_SEC * \
                self.config.buffer_size * \
                self.config.num_of_connections // \
                self.config.max_speed
            self.delay_time_for_process['sec'] = delay // Process.NSECs_IN_1_SEC
            self.delay_time_for_process['nsec'] = delay % Process.NSECs_IN_1_SEC

    def set_output_filename(self):
        ''' Set output filename using the filename in the URL '''
        self.output_filename = unquote(self.conns[0].filename)
        if self.output_filename == '':
            # This happens when we download index page.
            self.output_filename = self.config.default_filename

    def clobber_existing_file(self):
        if self.config.no_clobber and os.path.isfile(self.output_filename):
            if os.path.isfile(''.join([self.output_filename, '.st'])):
                self.add_message(f'Incomplete download found for {self.output_filename}, \
                    ignoring no-clobber option.\n')
            else:
                self.add_message(f'File {self.output_filename} already exists, not downloading.')
                # Is this necessary?
                self.ready = False
                return False
        return True

    # map axel_new()
    def new_preparation(self, url):
        '''
        Do preparation for the downloading, including:
        Get resource information by sending a GET request to the target URL
        and analysing the response.
        Reviewed on 5/22/2020, the HTTP redirects to FTP need to be added here.
        '''
        self.url = url
        self.tuning_params()
        self.prepare_1st_connection()
        self.conns[0].set_url(url)

        self.set_output_filename()
        if not self.clobber_existing_file():
            return False

        while True:
            if False in (self.conns[0].connection_init(), self.conns[0].get_resource_info()):
                # Is this necessary?
                self.ready = False
                return False

            if not self.conns[0].redirect_to_ftp:
                break

            # This is for redirection from HTTP to FTP,
            # which could only happen once, as FTP can't
            # be redirected back to HTTP.
            # Handle HTTP redirects to FTP here...
            pass

        # Always use the filename we got from HTTP response, if there is one.
        if self.conns[0].output_filename:
            self.output_filename = self.conns[0].output_filename

        if PYXEL_DEBUG:
            print(f'Before calling {__name__}, the url was {self.url}')
        # Reset url after getting the HTTP response, as it might be redirected.
        self.conns[0].url = self.conns[0].generate_url()
        self.url = self.conns[0].url
        if PYXEL_DEBUG:
            print(f'After calling {__name__}, the url is {self.url}')

        # Set file size from HTTP response.
        self.file_size = self.conns[0].file_size
        if self.config.verbose:
            if self.file_size != Connection.MAX_FILESIZE:
                self.add_message(f'File size: {self.file_size} bytes.')
            else:
                self.add_message('File size: unavailable.')
        return True

    # map axel_open()
    def open_local_files(self):
        '''
        Open a local file to store the downloaded data.
        Reviewed on 5/22/2020
        '''
        self.output_fd = None
        if self.config.verbose:
            self.add_message(f'Opening output file {self.output_filename}')
        self.state_filename = ''.join([self.output_filename, '.st'])

        # Check if server knows about RESTart and switch back to single connection
        # download if necessary.
        if not self.conns[0].resuming_supported:
            self.set_single_connection()

        if self.restore_state():
            self.output_fd = self.open_file(self.output_filename, os.O_WRONLY)
            if self.output_fd is None:
                return False
        else:
            self.output_fd = self.open_file(self.output_filename, os.O_CREAT | os.O_WRONLY)
            if self.output_fd is None:
                return False
            self.divide()
            if self.config.num_of_connections > 1:
                self.check_seek_past_eof()
        return True

    def check_seek_past_eof(self):
        ''' 
        Check whether the fs can handle seeks to past EOF areas.
        For most or all fs, this might be not needed.
        '''
        pass

    def start_downloading(self):
        for conn in self.conns:
            conn.set_url(self.url)
            conn.resuming_supported = True

        if self.config.verbose:
            print('Starting download...')

        for i in range(self.config.num_of_connections):
            if self.conns[i].current_byte > self.conns[i].last_byte:
                conn.lock.acquire()
                self.reactivate_connection(i)
                conn.lock.release()
            elif self.conns[i].current_byte < self.conns[i].last_byte:
                if self.config.verbose:
                    self.add_message(
                        f'Connection {i} downloading from '
                        f'{self.conns[i].host}:{self.conns[i].port} '
                        f'using interface {self.conns[i].local_ifs}'
                    )
                self.conns[i].state = True
                self.conns[i].setup_thread = threading.Thread(
                    target=self.setup_connection_thread,
                    args=(self.conns[i],)
                )
                self.conns[i].setup_thread.start()

        # The real downloading starts from here.
        self.start_time = time.time()
        self.ready = True

    @staticmethod
    def setup_connection_thread(conn):
        '''
        Thread used to set up a connection
        Reviewed on 5/22/2020
        '''
        conn.lock.acquire()
        if conn.request_setup():
            conn.last_transfer = time.time()
            if conn.execute_req_resp():
                conn.last_transfer = time.time()
                conn.enabled = True
            else:
                conn.disconnect()
        else:
            conn.disconnect()
        conn.state = False
        conn.lock.release()

    def __cancel_thread(self, thread_id):
        if not isinstance(thread_id, ctypes.c_long):
            thread_id = ctypes.c_long(thread_id)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id,
            ctypes.py_object(SystemExit)
        )
        if res == 0:
            raise ValueError('Invalid thread id')
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                thread_id,
                None
            )
            sys.stderr.write('Exception raise within thread failed\n')

    def reactivate_connection(self, i):
        ''' 
        reactivate the connection to find some more work to do 
        this function only changes current_byte and last_byte if it can
        Went through on 5/21/2020
        '''
        max_remaining = 0
        max_index = None

        if self.conns[i].enabled or self.conns[i].current_byte < self.conns[i].last_byte:
            return

        for conn_i, conn in enumerate(self.conns):
            if conn_i == i:
                continue
            remaining = conn.last_byte - conn.current_byte
            if remaining > max_remaining:
                max_remaining = remaining
                max_index = conn_i
        
        # Do not reactivate unless large enough
        if max_index and max_remaining > self.MIN_CHUNK_WORTH:
            if PYXEL_DEBUG:
                print(f'Reactivate connection {i}')
            self.conns[i].last_byte = self.conns[max_index].last_byte
            self.conns[max_index].last_byte = self.conns[max_index].current_byte + max_remaining // 2
            self.conns[i].current_byte = self.conns[max_index].last_byte

    def open_file(self, filename, mode):
        try:
            return os.open(self.output_filename, mode, 0o666)
        except Exception as e:
            self.add_message('Error opening local file. {}'.format(e.args[-1]))
            return None

    def restore_state(self):
        if not self.conns[0].resuming_supported:
            return False
        state = self.load_state()
        if state:
            self.config.num_of_connections = int(state['num_of_connections'])
            self.bytes_done = int(state['bytes_done'])
            assert self.config.num_of_connections > 0
            self.prepare_other_connections()
            for i in range(self.config.num_of_connections):
                print(state['connections'][i])
                self.conns[i].current_byte = state['connections'][i]['current_byte']
                self.conns[i].last_byte = state['connections'][i]['last_byte']
            self.add_message(
                f'State file found: {self.bytes_done} bytes downloaded, {self.file_size - self.bytes_done} to go.'
            )
            return True
        return False

    def set_single_connection(self):
        self.add_message(
            'Server doen\'t support resuming, '
            'starting from scratch with one connection.'
        )
        self.config.num_of_connections = 1

    def optimize_num_of_connections(self):
        ''' Optimize the number of connections in case the file is small. '''
        max_conns = max(1, self.file_size // self.MIN_CHUNK_WORTH)
        if max_conns < self.config.num_of_connections:
            self.config.num_of_connections = max_conns

    def divide(self):
        '''
        Divide the file and set locations for each connection.
        Set followings,
        num_of_connections, current_byte, last_byte
        '''
        self.optimize_num_of_connections()
        self.prepare_other_connections()

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
        if remaining_bytes:
            self.conns[-1].last_byte += remaining_bytes

        if PYXEL_DEBUG:
            for i in range(self.config.num_of_connections):
                print('Downloading {0}-{1} using conn: {{{2}}}'.format(
                    self.conns[i].current_byte,
                    self.conns[i].last_byte,
                    i
                ))

    def add_message(self, message):
        self.messages.append(message)

    def create_state_file_periodically(self):
        ''' Create state file periodically. '''
        if time.time() > self.next_state:
            self.save_state()
            self.next_state = current_time + self.config.save_state_interval

    def connections_check(self):
        ''' Look for aborted connections and attempt to restart them. '''
        for i, conn in enumerate(self.conns):
            if not conn.lock.acquire(blocking=False):
                continue
            if not conn.enabled and conn.current_byte < conn.last_byte:
                if not conn.state:
                    # Wait for termination of this thread
                    conn.setup_thread.join()

                    if self.config.verbose:
                        self.add_message('Connection {0} downloading from {1}:{2} using interface {3}'
                            .format(i, conn.host, conn.port, conn.local_ifs))
                    conn.state = True
                    conn.setup_thread = threading.Thread(
                        target=self.setup_connection_thread,
                        args=(conn,)
                    )
                elif time.time() > conn.last_transfer + self.config.reconnect_delay:
                    self.__cancel_thread(conn.setup_thread)
                    conn.state = False
                    conn.setup_thread.join()
            conn.lock.release()

    def calculate_average_speed_and_finish_time(self):
        self.bytes_per_second = (self.bytes_done - self.start_byte) // (time.time() - self.start_time)
        if self.bytes_per_second != 0:
            self.finish_time = int(
                self.start_time + (self.file_size - self.start_time) / self.bytes_per_second
            )
        else:
            self.finish_time = None

    def adjust_downloading_speed(self):
        if self.config.max_speed <= 0:
            return
        max_speed_ratio = 1000 * self.bytes_per_second / self.config.max_speed
        if max_speed_ratio > 1000 * self.DELAY_ADJUST_PERCENT:
            self.delay_time_for_process["nsec"] += 0

    def check_if_bytes_done(self):
        if self.bytes_done == self.file_size:
            self.ready = True

    def downloading_maintance(self):
        self.connections_check()
        self.calculate_average_speed_and_finish_time()
        self.adjust_downloading_speed()
        self.check_if_bytes_done()

    def do_downloading(self):
        self.create_state_file_periodically()

        ready_connections = self.wait_for_data()

        if not ready_connections:
            Process.process_sleep(Process.delay_time_for_waiting_connection)
            self.downloading_maintance()
            return

    def wait_for_data(self):
        ''' Wait data on (one of) the connections '''
        ready_connections = []
        for conn in self.conns:
            # Skip connection if setup thread hasn't released the lock yet.
            # enabled is shared variable.
            if not conn.lock.acquire(blocking=False):
                if conn.enabled and conn.is_connected()
                    ready_connections.append(conn)
                conn.lock.release()
        return ready_connections

    def terminate(self):
        ''' 
        Terminate a downloading process
        Reviewed on 5/22/2020
        '''
        for conn in self.conns:
            if conn.setup_thread:
                self.__cancel_thread(conn.setup_thread.ident)
                conn.setup_thread.join()
            conn.disconnect()

        if self.ready and os.path.exists(self.state_filename):
            os.unlink(self.state_filename)
        elif self.bytes_done > 0:
            self.save_state()

        os.close(self.output_fd)

    def save_state(self):
        # No use for .st file if the server doesn't support resuming.
        if not self.conns[0].resuming_supported:
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
        with open(self.state_filename, 'w') as file_obj:
            json.dump(state, file_obj)

    def load_state(self):
        if os.path.exists(self.state_filename):
            with open(self.state_filename, 'r') as file_obj:
                return json.load(file_obj)
        return None

    @staticmethod
    def process_sleep(delay):
        delay_in_seconds = delay['sec'] + delay['nsec'] / Process.NSECs_IN_1_SEC
        if delay_in_seconds <= Process.SMALLEST_DELAY_IN_SEC:
            delay_in_seconds = Process.SMALLEST_DELAY_IN_SEC
        time.sleep(delay_in_seconds)