#!/usr/bin/python3
from urllib.parse import quote
from tcp import Tcp

class Connection(object):
    PROTOCOL_FTP = 0
    PROTOCOL_HTTP = 1

    FTPS = {'is_secure': True, 'protocol': Connection.PROTOCOL_FTP}
    FTP = {'is_secure': False, 'protocol': Connection.PROTOCOL_FTP}
    HTTPS = {'is_secure': True, 'protocol': Connection.PROTOCOL_HTTP}
    HTTP = {'is_secure': False, 'protocol': Connection.PROTOCOL_HTTP}

    FTP_PORT = 21
    FTPS_PORT = 990
    HTTP_PORT = 80
    HTTPS_PORT = 443

    DEFAULT_PROTOCOL = Connection.HTTP
    DEFAULT_PORT = Connection.HTTP_PORT

    def __init__(self, config, url):
        self.config = config
        self.url = url
        self.parse_url()

    def connection_init(self):
        http_proxy = self.config.http_proxy
        hosts = self.config.no_proxy
        proxy = None

        if http_proxy == '':
            proxy = ''
        elif host != '':

    def get_info(self):
        pass

    def parse_url(self):
        rest_of_url = self.set_protocol_and_port()
        slash_index = rest_of_url.find('/')
        if slash_index == -1:
            self.dir = '/'
        else:
            self.dir = rest_of_url[slash_index:]
            if self.protocol == Connection.HTTP or self.protocol == Connection.HTTPS:
                self.dir = quote(self.dir)

    def set_protocol_and_port(self):
        if '://' not in self.url:
            self.protocol = Connection.DEFAULT_PROTOCOL
            self.port = Connection.DEFAULT_PORT
            return self.url
        else:
            protocol_str, rest_of_url = self.url.split('://')
            if protocol_str.lower() == 'ftp':
                self.protocol = Connection.FTP
                self.port = Connection.FTP_PORT
            elif protocol_str.lower() == 'ftps':
                self.protocol = Connection.FTPS
                self.port = Connection.FTPS_PORT
            elif protocol_str.lower() == 'http':
                self.protocol = Connection.HTTP
                self.port = Connection.HTTP_PORT
            elif protocol_str.lower() == 'https':
                self.protocol = Connection.HTTPS
                self.port = Connection.HTTPS_PORT
            return rest_of_url

    def generate_url(self):
        url_scheme = Connection.get_url_scheme_from_protocol(self.protocol)


    @staticmethod
    def get_url_scheme_from_protocol(protocol):
        if protocol == Connection.FTP:
            return 'ftp://'
        elif protocol == Connection.FTPS:
            return 'ftps://'
        elif protocol == Connection.HTTP:
            return 'http://'
        elif protocol == Connection.HTTPS:
            return 'https://'
