#!/usr/bin/python3
import re
from urllib.parse import quote
from urllib.parse import urlparse
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
        parse_results = urlparse(self.url)
        self.parse_scheme(parse_results.scheme)
        self.parse_netloc(parse_results.netloc)
        self.parse_path(parse_results.path)

    def parse_path(self, path):
        self.dir, self.file = re.compile('^(.*/)([^/]*)$').findall(quote(path))

    def parse_user_and_password(self, netloc):
        split_result = netloc.split('@')
        if len(split_result) < 2:
            if self.scheme['protocol'] == Connection.PROTOCOL_FTP:
                self.user = 'anonymous'
                self.password = 'anonymous'
            else:
                self.user = ''
                self.password = ''
            return split_result
        else:
            self.user, self.password = split_result[0].split(':')
            return split_result[1]

    def parse_domain_and_port(self, rest_of_netloc):
        if rest_of_netloc.startswith('['):
            self.domain, port = re.compile('^(\[.+\]):{0,1}([0-9]*)$').findall(rest_of_netloc)[0]
            if port != '':
                self.port = int(port)
        else:
            split_result = rest_of_netloc.split(':')
            if len(split_result) > 1:
                self.domain = split_result[0]
                self.port = split_result[1]
            else:
                self.domain = split_result

    def parse_netloc(self, netloc):
        rest_of_netloc = self.parse_user_and_password(netloc)
        self.parse_domain_and_port(rest_of_netloc)

    def parse_scheme(self, scheme):
        if scheme.lower() == 'ftp':
            self.scheme = Connection.FTP
            self.port = Connection.FTP_PORT
        elif scheme.lower() == 'ftps':
            self.scheme = Connection.FTPS
            self.port = Connection.FTPS_PORT
        elif scheme.lower() == 'http':
            self.scheme = Connection.HTTP
            self.port = Connection.HTTP_PORT
        elif scheme.lower() == 'https':
            self.scheme = Connection.HTTPS
            self.port = Connection.HTTPS_PORT

    def generate_url(self):
        url = Connection.get_scheme(self.scheme)
        if self.user != '' and self.password != '':
            url = ''.join([url_scheme, self.user, ':', self.password, '@'])
        return ''.join([url, self.domain, ':', str(self.port), self.dir, self.file])

    @staticmethod
    def get_scheme(protocol):
        if protocol == Connection.FTP:
            return 'ftp://'
        elif protocol == Connection.FTPS:
            return 'ftps://'
        elif protocol == Connection.HTTP:
            return 'http://'
        elif protocol == Connection.HTTPS:
            return 'https://'
