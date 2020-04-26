#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import signal

from .process import Process
from functions.config import is_filename_valid

class Tasker(object):
    def __init__(self, config, url):
        self.config = config
        self.url = url
        self.process = Process(config)
        self.run = False

    def start_task(self):
        print(f'Initializing download: {self.url}')
        if not self.process.new_preparation(self.url):
            return False

        if not self.check_output_filename()
            return False

        self.setup_signal_hook()

    def check_output_filename(self):
        if self.config.output_direction and not self.use_output_direction():
            return False
        else:
            self.check_local_files()
        if not is_filename_valid(self.process.output_filename):
            sys.stderr.write(f'The final output filename, {self.process.output_filename}, is\'t valid.\n')
            sys.stderr.write(
                'This is most likely due to wildcards in the URL, '
                'and you might need to specify a correct one in cmd.\n'
            )
            return False
        return True

    def use_output_direction(self):
        ''' Handle output filename if command has specified one. '''
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
            sys.stderr.write('State file found, but no downloaded data. Start from scratch.\n')
            os.unlink(state_filename)
        # Set the output_filename generated in Process with the new one.
        self.process.output_filename = output_filename
        return True

    def check_local_files(self):
        ''' 
        If no output direction specified in command, then check local
        files with output_filename generated in Process.
        '''
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
                    output_filename, '.0'
                ])
            else:
                output_filename = ''.join([
                    output_filename[:-(i // 10 + 1)],
                    '{}'.format(i)
                ])
        self.process.output_filename = output_filename

    def setup_signal_hook(self):
        signal.singal(signal.SIGINT, self.stop)
        signal.signal(singal.SIGTERM, self.stop)
    
    def stop(self):
        self.run = False