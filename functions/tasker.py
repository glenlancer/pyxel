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

        # Flag to determine if the program shall run. It might be set as False by signals
        self.run = True

    def start_task(self):
        ''' The program\'s main logic '''
        sys.stdout.write(f'Initializing download: {self.url}\n')

        if not self.process.new_preparation(self.url):
            return False

        if not self.check_output_filename()
            return False

        if not self.process.open_local_files()
            return False

        self.setup_signal_hook()

        # TBD.

    def check_output_filename(self):
        ''' To finalize the output file name to be used '''
        if self.config.output_filename_from_cmd and not self.use_output_filename_from_cmd():
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

    def use_output_filename_from_cmd(self):
        ''' 
        Handle output filename if command has specified one
        The logic for output file speified from command:
        1) If the file exists, but no state file found, the program won't continue
        2) If the file doesn't exist, but state file exists, then, delete the state file and continue
        3) Other scenarios are okay
        '''
        output_filename = self.config.output_filename_from_cmd
        # If the command specified a directory, then, the filename is this directory combined
        # output_filename already derived from Process()
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
        # If we want to download data into an existing file, then, resuming must be supported
        # and the state file must exist
        if os.path.exists(output_filename) and not os.path.exists(state_filename):
            sys.stderr.write('No state file, cannot resume!\n')
            return False
        # If we see a state file but no output file, then, delete the state file and start from scrach
        if os.path.exists(state_filename) and not os.path.exists(output_filename):
            sys.stderr.write('State file found, but no downloaded data. Start from scratch.\n')
            os.unlink(state_filename)
        # Replace the output_filename generated in Process with the new one from command
        self.process.output_filename = output_filename
        return True

    def check_local_files(self):
        ''' 
        If no output filename specified in command, then check local
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
            if f_exists and st_exists and self.process.is_resuming_supported():
                # If file exists, we'll continue only if we can write it, otherwise jump it
                break
            elif not st_exists:
                # If we invent a new file name, we'll continue only if
                # there is no state file, otherwise jump it
                break
            # We'll continue if file can be written or file and state file pair is brand new
            if len(output_filename) == length:
                output_filename = ''.join([
                    output_filename, '.0'
                ])
            else:
                output_filename = ''.join([
                    output_filename[:-len(str(i-1))],
                    str(i)
                ])
            i += 1
        self.process.output_filename = output_filename

    def setup_signal_hook(self):
        '''
        SIGINT: notmally associate with Ctrl + C
        SIGTERM: the default signal sent to a process by the kill or killall commands
        SIGKILL: this signal cannot be caught or ignored
        '''
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(singal.SIGTERM, self.stop)
    
    def stop(self):
        '''
        Use this function to replace signals' default behaviors, by setting run as False
        will tell the program to terminate after everthing necessary thing is settled.
        '''
        sys.stdout.write('SIGINT or SIGTERM signal recevied, stop running the progam.\n')
        self.run = False