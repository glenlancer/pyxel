#!/usr/bin/python3
import socket

class Config(object):
    __MAX_REDIRECT = 20
    __DEFAULT_IO_TIMEOUT = 120
    __DEFAULT_USER_AGENT = 'Mozilla/5.0 3578.98 Safari/537.36'
    #AF_INET = socket.AF_INET
    #AF_INET_6 = socket.AF_INET6

    def __init__(self):
        self.default_filename = 'default'
        self.output = ''
        self.http_proxy = ''
        self.no_proxy = ''
        self.strip_cgi_parameters = 1
        self.save_state_interval = 10
        self.connection_timeout = 45
        self.reconnect_delay = 20
        self.num_of_connections = 4
        self.max_redirect = Config.__MAX_REDIRECT
        self.io_timeout = Config.__DEFAULT_IO_TIMEOUT
        self.buffer_size = 5120
        self.max_speed = 0
        self.verbose = 1
        self.insecure = 0
        self.no_clobber = 0
        self.do_search = False
        self.search_timeout = 10
        self.search_threads = 3
        self.search_amount = 15
        self.search_top = 3
        self.ai_family = socket.AF_UNSPEC
        self.__headers = {}
        self.add_header('User-Agent', self.__DEFAULT_USER_AGENT)
        self.interfaces = []

    def add_header(self, key, value):
        self.__headers[key] = value

    def set_protocol(self, protocol):
        if protocol.lower() == 'ipv4':
            self.ai_family = socket.AF_INET
        elif protocol.lower() == 'ipv6':
            self.ai_family == socket.AF_INET6
        else:
            raise Exception(f'Exception in {__name__}: unsupported protocol.')
    
    
