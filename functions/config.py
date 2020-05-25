#!/usr/bin/python3

import re
import socket

PYXEL_DEBUG = False

def is_filename_valid(file_name):
    ''' check if given filename is valid '''
    chars = '^[\-_\.a-zA-Z0-9\,\s]*$'
    return re.match(chars, file_name)

class Config(object):
    # Max Http redirect
    __MAX_REDIRECT = 20
    # Time out for select(), in seconds
    __DEFAULT_IO_TIMEOUT = 120
    __DEFAULT_USER_AGENT = 'Mozilla/5.0 3578.98 Safari/537.36'
    AF_UNSPEC = socket.AF_UNSPEC

    def __init__(self):
        self.default_filename = 'pyxel_gathering.bin'
        # Store the output filename from command
        self.output_filename_from_cmd = None
        # Store the URL of http proxy
        self.http_proxy = None
        # A list of domains that don't use proxies
        self.no_proxies = []
        self.strip_cgi_parameters = True
        # Interval to save state file for downloading, in seconds
        self.save_state_interval = 10
        self.connection_timeout = 45
        self.reconnect_delay = 20
        self.num_of_connections = 4
        self.max_redirect = Config.__MAX_REDIRECT
        self.io_timeout = Config.__DEFAULT_IO_TIMEOUT
        self.buffer_size = 5120
        self.max_speed = 0
        self.verbose = False
        self.alternate_output = False
        self.insecure = False
        self.no_clobber = False
        self.ai_family = Config.AF_UNSPEC
        self.headers = {}
        self.set_header('User-Agent', self.__DEFAULT_USER_AGENT)
        # A list of local interfaces, currently only use 1, i.e. the wireless card
        self.interfaces = ['wlo1']
        self.standard_output = None

    def set_header(self, key, value):
        self.headers[key] = value

    def set_protocol(self, protocol):
        if protocol.lower() == 'ipv4':
            self.ai_family = socket.AF_INET
        elif protocol.lower() == 'ipv6':
            self.ai_family == socket.AF_INET6
        else:
            raise Exception(f'Exception in {__name__}: unsupported protocol.')

    def parse_interfaces(self):
        pass
