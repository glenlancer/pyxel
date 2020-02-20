#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re

from .tcp import Tcp
from .connection import Connection

'''
ftp://用户名:密码@FTP服务器IP或域名:FTP命令端口/路径/文件名
'''

class Ftp(Connection):
    FTP_PASSIVE = 1
    FTP_PORT = 2

    def __init__(
        self,
        ai_family, io_timeout, local_ifs=None):
        super(Ftp, self).__init__(ai_family, io_timeout, local_ifs)
        
        self.cwd = ''
        self.message = None # message belongs to Ftp()
        self.status = None
        self.data_tcp = Tcp()
        self.protocol = ''
        self.ftp_mode = self.FTP_PASSIVE
        self.local_if = ''

    def connect(self):
        if not self.tcp.connect(
            self.host,
            self.port,
            self.is_secure_scheme(),
            self.ai_family,
            self.io_timeout,
            self.local_ifs):
            return False

    def cwd(self, cwd):
        self.send_command(f'CWD {cwd}')

    # Read status from server.
    def ftp_wait(self):
        self.message = ''
        complete = None
        while True:
            while True:
                try:
                    recv_char = self.tcp.recv(1).decode('utf-8')
                except RuntimeError as r:
                    sys.stderr.write('Connection gone.\n')
                    sys.stderr.write(f'{r.message}\n')
                    return -1
                self.message = ''.join([self.message, recv_char])
                if not self.message or self.message[-1:] == '\n':
                    break
            res = re.findall('^([0-9]{3}) .*$', self.message)
            if len(res) == 1:
                self.status_code = res[0]
                complete = 1
            else:
                complete = 0

            
            if complete == 2:
                break

    def ftp_command(self, cmd):
        cmd = ''.join([cmd, '\r\n'])
        try:
            self.tcp.send(cmd.encode('utf-8'))
        except RuntimeError as r:
            sys.stderr.write(f'Error writing command {cmd}')
            sys.stderr.write(f'{r.message}\n')
            return False
        return True