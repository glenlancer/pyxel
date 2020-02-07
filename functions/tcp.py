#!/usr/bin/python3
import socket

class Tcp(object):
    def __init__(self):
        self.socket_ref = None
        self.ai_family = socket.AF_UNSPEC
        pass
    
    def connect(self, hostname, port, is_secure, local_if, io_timeout) {
        if local_if:
            if self.ai_family != socket.AF_INET:
                local_if = None
            else:
                
    }

    @staticmethod
    def print_error(hostname, port, reason):
        print(f'Unable to connect to server {hostname}:{port} {reason}')

    @staticmethod
    def is_valid_address(address, socket_type):
        try:
            socket.inet_pton(socket_type, address)
        except socket.error:
            return False
        return True
