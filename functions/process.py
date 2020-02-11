#!/usr/bin/python3

class Process(object):
    def __init__(self, config):
        self.config = config
        self.url = self.config.command_url

    def new_process(self):
        pass

    def open_process(self):
        pass