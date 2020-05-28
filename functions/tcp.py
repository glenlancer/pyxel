#!/usr/bin/python3
# -*- coding: utf-8 -*-

# HowTo
# https://docs.python.org/3.8/howto/sockets.html#socket-howto

import ssl
import socket
import struct
import psutil
import select

class Tcp(object):
    def __init__(self):
        self.socket_fd = None

    def is_connected(self):
        return self.socket_fd != None

    def connect(self, host, port, is_secure, ai_family, io_timeout, local_if=None):
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
            Tcp.print_error(host, port, e.message)
            return False
        for gai_result in gai_results:
            t_ai_family, ai_sockettype, ai_protocol, _, (ai_host, ai_port) = gai_result
            try:
                self.close()
                self.socket_fd = socket.socket(
                    t_ai_family,
                    ai_sockettype,
                    ai_protocol
                )
                #if is_secure:
                #    context = ssl.SSLContext()
                #    self.socket_fd = context.wrap_socket(
                #        self.socket_fd, server_hostname=ai_host
                #    )
                # Does this mean the port number is dynamic allocated?
                # Do we need to do this: if local_if is not None and t_ai_family == socket.AF_INET:
                if local_if:
                    local_addr = self.get_if_ip(local_if, t_ai_family)
                    if local_addr:
                        self.socket_fd.bind((local_addr, 0))
                self.socket_fd.setblocking(False)
                self.socket_fd.settimeout(io_timeout)
                self.socket_fd.setsockopt(socket.IPPROTO_TCP, socket.TCP_FASTOPEN, 1)
                self.socket_fd.connect((ai_host, ai_port))
            except socket.error as e:
                Tcp.print_error(host, port, e.args[-1])
                self.socket_fd = None
            if self.socket_fd is None:
                continue
            _, writeable, _ = select.select([], [self.socket_fd], [], io_timeout)
            if self.socket_fd in writeable:
                break
        if self.socket_fd is None:
            return False
        # Same function as to use settimeout() ?
        # self.socket_fd.settimeout(io_timeout)
        # val = struct.pack('QQ', io_timeout, 0)
        # self.socket_fd.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, val)
        # self.socket_fd.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, val)
        return True

    def close(self):
        if self.socket_fd is not None:
            self.socket_fd.close()
            self.socket_fd = None

    def recv(self, msg_size):
        if self.socket_fd is None:
            raise Exception(f'Exception in {__name__}: socket_fd is None.')
        chunks = []
        bytes_recvd = 0
        while bytes_recvd < msg_size:
            chunk = self.socket_fd.recv(min(msg_size - bytes_recvd, 2048))
            if chunk == b'':
                # the server has closed the connection
                break
            chunks.append(chunk)
            bytes_recvd += len(chunk)
        return b''.join(chunks)

    def send(self, data):
        if self.socket_fd is None:
            raise Exception(f'Exception in {__name__}: socket_fd is None.')
        if not isinstance(data, bytes):
            raise Exception(f'Exception in {__name__}: incorrect data type for {data}')
        totalsent = 0
        msglen = len(data)
        while totalsent < msglen:
            sent = self.socket_fd.send(data[totalsent:])
            if sent == 0:
                raise RuntimeError(f'Socket connection broken while sending.\n{data}')
            totalsent += sent

    @staticmethod
    def print_error(hostname, port, reason):
        print(f'Unable to connect to server {hostname}:{port} {reason}')

    @staticmethod
    def is_valid_address(socket_type, address):
        try:
            socket.inet_pton(socket_type, address)
        except socket.error:
            return False
        return True

    @staticmethod
    def get_if_ip(local_if, ai_family):
        if_addrs = psutil.net_if_addrs()
        if local_if in if_addrs:
            for item in if_addrs[local_if]:
                if isinstance(item, psutil._common.snic) and item.family == ai_family:
                    return item.address
        return None
