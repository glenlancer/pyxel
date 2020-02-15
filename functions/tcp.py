#!/usr/bin/python3
# -*- coding: utf-8 -*-

# HowTo
# https://docs.python.org/3.8/howto/sockets.html#socket-howto

import socket
import struct

class Tcp(object):
    def __init__(self):
        self.socket_ref = None

    def is_connected(self):
        return self.socket_ref != None

    def connect(self, hostname, port, is_secure, ai_family, io_timeout, local_if=None):
        try:
            gai_results = socket.getaddrinfo(
                hostname,
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
                    ai_sockettype,
                    ai_protocol
                )
                self.socket_ref.setblocking(0)
                self.socket_ref.settimeout(io_timeout)
                # Does this mean the port number is dynamic allocated?
                #if local_if is not None and t_ai_family == socket.AF_INET:
                #    self.socket_ref.bind((local_if, 0))
                self.socket_ref.setsockopt(socket.IPPROTO_TCP, socket.TCP_FASTOPEN, 1)
                self.socket_ref.connect(ai_addr)
            except socket.error as e:
                Tcp.print_error(hostname, port, e.message)
                self.socket_ref = None
            if self.socket_ref is not None:
                break
        if self.socket_ref is None:
            return False
        # Same function as to use settimeout() ?
        # self.socket_ref.settimeout(io_timeout)
        val = struct.pack('QQ', io_timeout, 0)
        self.socket_ref.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, val)
        self.socket_ref.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, val)
        return True

    def close(self):
        if self.socket_ref is not None:
            self.socket_ref.shutdown(2)
            self.socket_ref.close()
            self.socket_ref = None

    def recv(self, msg_size):
        if self.socket_ref is None:
            raise Exception(f'Exception in {__name__}: socket_ref is None.')
        chunks = []
        bytes_recvd = 0
        while bytes_recvd < msg_size:
            chunk = self.socket_ref.recv(min(msg_size - bytes_recvd, 2048))
            if chunk == b'':
                raise RuntimeError('Socket connection broken while receiving.')
            chunks.append(chunk)
            bytes_recvd += len(chunk)
        return b''.join(chunks)

    def send(self, data):
        if self.socket_ref is None:
            raise Exception(f'Exception in {__name__}: socket_ref is None.')
        totalsent = 0
        msglen = len(data)
        while totalsent < msglen:
            sent = self.socket_ref.send(data[totalsent:])
            if sent == 0:
                raise RuntimeError(f'socket connection broken while sending.\n{data}')
            totalsent += sent

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