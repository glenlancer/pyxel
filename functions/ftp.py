#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .tcp import Tcp

class Ftp(object):
    FTP_PASSIVE = 1
    FTP_PORT = 2

    def __init__(self):
        self.cwd = ''
        self.message = ''
        self.status = None
        self.tcp = Tcp()
        self.data_tcp = Tcp()
        self.protocol = ''
        self.ftp_mode = self.FTP_PASSIVE
        self.local_if = ''
        pass

    