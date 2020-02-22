#!/usr/bin/python3
import socket

PYXEL_DEBUG = True

class Config(object):
    __MAX_REDIRECT = 20
    __DEFAULT_IO_TIMEOUT = 120
    __DEFAULT_USER_AGENT = 'Mozilla/5.0 3578.98 Safari/537.36'
    AF_UNSPEC = socket.AF_UNSPEC

    def __init__(self):
        self.default_filename = 'pyxel_gathering'
        self.output_filename = None
        self.http_proxy = None
        self.no_proxies = []
        self.strip_cgi_parameters = 1
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
        self.do_search = False
        self.search_timeout = 10
        self.search_threads = 3
        # Number of URL's to request from filesearching.com
        self.search_amount = 15
        self.search_top = 3
        self.ai_family = Config.AF_UNSPEC
        self.headers = {}
        self.set_header('User-Agent', self.__DEFAULT_USER_AGENT)
        self.interfaces = ['wlp1s0']
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

    def parse_interfaces():
        pass
