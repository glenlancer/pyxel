#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .tcp import Tcp

class Ftp(object):
    FTP_PASSIVE = 1
    FTP_PORT = 2

    def __init__(self, conn):
        self.conn = conn
        self.cwd = ''
        self.message = None # message belongs to Ftp()
        self.status = None
        self.tcp = Tcp()
        self.data_tcp = Tcp()
        self.protocol = ''
        self.ftp_mode = self.FTP_PASSIVE
        self.local_if = ''

    def connect(self):
        pass

    def cwd(self, cwd):
        self.send_command(f'CWD {cwd}')

    def wait(self):
        self.message = None
        

    def send_command(self, cmd):
        cmd = ''.join([cmd, '\r\n'])
        self.tcp.write(cmd)