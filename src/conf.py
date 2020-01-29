#!/usr/bin/python3

class Conf(object):
    __MAX_REDIRECT = 20
    __DEFAULT_IO_TIMEOUT = 120

    def __init__(self):
        self.default_filename = "default"
        self.http_proxy = ""
        self.no_proxy = ""
        self.strip_cgi_parameters = 1
        self.save_state_interval = 10
        self.connection_timeout = 45
        self.reconnect_delay = 20
        self.num_of_connections = 4
        self.max_redirect = Conf.__MAX_REDIRECT
        self.io_timeout = Conf.__DEFAULT_IO_TIMEOUT
        self.buffer_size = 5120
        self.max_speed = 0
        self.verbose = 1
        self.insecure = 0
        self.no_clobber = 0
        self.search_timeout = 10
        self.search_threads = 3
        self.search_amount = 15
        self.search_top = 3
        self.ai_family = "AF_UNSPEC"
        
        pass
