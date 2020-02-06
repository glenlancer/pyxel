#!/usr/bin/python3

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

    def __init__(self, config):
        self.config = config
    
    def parse_protocol_and_port(self, url):
        if '://' not in url:
            self.protocol = Connection.DEFAULT_PROTOCOL
            self.port = Connection.DEFAULT_PORT
        else:
            protocol_str, _ = url.split('://')
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

        
