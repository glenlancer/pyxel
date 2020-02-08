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
# http://www.example.com:80/path/to/myfile.html?key1=value1&key2=value2#SomewhereInTheDocument
# ftp://用户名：密码@站点地址 例如：ftp://test:test@192.168.0.1:21/profile
# http://[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80/index.html
    def get_info(self):
        pass

    def parse_url(self):
        rest_of_url = self.set_protocol_and_port()
        self.parse_dir_and_filename(rest_of_url)

    @staticmethod
    def remove_url_after(rest_of_url, split_str):
        url_results = rest_of_url.split(split_str)
        if len(url_results) > 1:
            return url_results[0]
        return rest_of_url

    def parse_user_and_password(self, rest_of_url):
        if self.protocol not in (self.FTP, self.FTPS):
            self.user = ''
            self.password = ''
        else:
            url_results = rest_of_url.split('@')


    def parse_dir_and_filename(self, rest_of_url):
        rest_of_url = Connection.remove_url_after(rest_of_url, '#')
        rest_of_url = Connection.remove_url_after(rest_of_url, '?')
        first_slash_index = rest_of_url.find('/')
        last_slash_index = rest_of_url.rfind('/')
        if first_slash_index != last_slash_index:
            self.dir = rest_of_url[first_slash_index:last_slash_index]
            self.file = rest_of_url[last_slash_index + 1:]
        else:
            self.dir = '/'
            self.file = ''

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
