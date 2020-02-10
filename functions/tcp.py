#!/usr/bin/python3
import socket

class Tcp(object):
    def __init__(self, config):
        self.config = config
        self.socket_ref = None
        self.ai_family = self.config.ai_family

    def connect(self, hostname, port, is_secure, local_if=None):
        try:
            gai_results = socket.getaddrinfo(
                host,
                port,
                self.ai_family,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                socket.AI_PASSIVE
            )
        except socket.gaierror as e:
            Tcp.print_error(hostname, port, e.message)
            return False
        for gai_result in gai_results:
            ai_family, ai_sockettype, ai_protocol, _, ai_addr = gai_result
            try:
                self.close()
                self.socket_ref = socket.socket(
                    ai_family,
                    socket_type,
                    ai_protocol
                )
                # Does this mean the port number is dynamic allocated?
                if local_if is not None and ai_family == socket.AF_INET:
                    self.socket_ref.bind((local_if, 0))
                self.socket_ref.setsockopt(socket.IPPROTO_TCP, socket.TCP_FASTOPEN, None, 0)
                self.socket_ref.connect(ai_addr)
                # https://www.cnblogs.com/zhiyong-ITNote/p/7553694.html Check this !!!
            except socket.error as e:
                Tcp.print_error(hostname, port, e.message)
                return False

    def close(self):
        if self.socket_ref is not None:
            self.socket_ref.close()
            self.socket_ref = None

    def read(self):
        pass

    def write(self):
        pass

    def get_interface_ip(self):
        pass

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
