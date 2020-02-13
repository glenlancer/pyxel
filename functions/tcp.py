#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket

class Tcp(object):
    def __init__(self, buffer_size):
        self.socket_ref = None
        self.buffer_size = buffer_size

    def connect(self, hostname, port, is_secure, ai_family, io_timeout, local_if=None):
        try:
            gai_results = socket.getaddrinfo(
                host,
                port,
                ai_family,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                socket.AI_ADDRCONFIG
            )
        except socket.gaierror as e:
            Tcp.print_error(hostname, port, e.message)
            return False
        for gai_result in gai_results:
            t_ai_family, ai_sockettype, ai_protocol, _, ai_addr = gai_result
            try:
                self.close()
                self.socket_ref = socket.socket(
                    t_ai_family,
                    socket_type,
                    ai_protocol
                )
                self.socket_ref.setblocking(0)
                self.socket_ref.settimeout(io_timeout)
                # Does this mean the port number is dynamic allocated?
                if local_if is not None and t_ai_family == socket.AF_INET:
                    self.socket_ref.bind((local_if, 0))
                self.socket_ref.setsockopt(socket.IPPROTO_TCP, socket.TCP_FASTOPEN, 1)
                self.socket_ref.connect(ai_addr)
            except socket.error as e:
                Tcp.print_error(hostname, port, e.message)
                self.socket_ref = None
            if self.socket_ref is not None:
                break
        if self.socket_ref is None:
            return False
        self.socket_ref.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, io_timeout)
        self.socket_ref.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, io_timeout)
        return True

    def close(self):
        if self.socket_ref is not None:
            self.socket_ref.shutdown(2)
            self.socket_ref.close()
            self.socket_ref = None

    def read(self):
        if self.socket_ref is None:
            raise Exception(f'Exception in {__name__}: socket_ref is None.')
        return self.socket_ref.recv(self.buffer_size)

    def write(self, data):
        if self.socket_ref is None:
            raise Exception(f'Exception in {__name__}: socket_ref is None.')
        return self.socket_ref.send(data)

    @staticmethod
    def print_error(hostname, port, reason):
        print(f'Unable to connect to server {hostname}:{port} {reason}')

    @staticmethod
    def is_valid_address(socket_type, adress):
        try:
            socket.inet_pton(socket_type, address)
        except socket.error:
            return False
        return True

    def get_interface_ip(self, interface):
        pass