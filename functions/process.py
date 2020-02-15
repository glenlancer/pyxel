#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Process(object):
    def __init__(self, config):
        self.config = config
        self.url = self.config.command_url
        self.messages = []
        self.buffer_filename = ''

    def new_process(self):
        pass

    def open_process(self):
        if self.config.verbose:
