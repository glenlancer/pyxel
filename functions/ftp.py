#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re

from .tcp import Tcp
from .connection import Connection

class Ftp(Connection):
    '''
    FTP Url example:
    ftp://username:password@'ftp server domain or IP':port/path/to/file
    '''
    FTP_PASSIVE = 1
    # FTP PORT is not supported
    FTP_PORT = 2

    def __init__(
        self,
        ai_family, io_timeout, max_redirect, local_ifs=None):
        super(Ftp, self).__init__(ai_family, io_timeout, max_redirect, local_ifs)
        self.cwd = ''
        self.ftp_replies = []
        self.data_tcp = Tcp()
        # Only FTP_PASSIVE implemented.
        # self.ftp_mode = self.FTP_PASSIVE
        self.local_if = ''

    def is_data_connected(self):
        return self.data_tcp.is_connected()

    def connect(self):
        if not self.tcp.connect(
            self.host,
            self.port,
            self.is_secure_scheme(),
            self.ai_family,
            self.io_timeout,
            self.local_ifs):
            return False
        if self.is_wait_nok(2):
            return False
        self.ftp_command(f'USER {self.user}')
        if self.is_wait_nok(2):
            if self.status_code // 100 == 3:
                self.ftp_command(f'PASS {self.password}')
                if self.is_wait_nok(2):
                    return False
            else:
                return False
        # Just use Binary... not ASCII mode.
        self.ftp_command('TYPE I')
        if self.is_wait_nok(2):
            return False
        return True

    def ftp_data_connect():
        '''
        Open a data connection; Only passive mode supported.
        Passive mode reply example:
        227 Passive mode on (115,47,68,228,35,40)
        '''
        if self.is_data_connected():
            return False
        self.ftp_command('PASV')
        if self.is_wait_nok(2) or len(self.ftp_replies) != 1:
            sys.stderr.write(f'Ftp reply for PASV incorrect: {self.ftp_replies}')
            return False
        try:
            res_data = re.findall('^.*\((.*)\)$', self.ftp_replies[0])[0]
            ip1, ip2, ip3, ip4, port1, port2 = res_data.split(',')
            host = f'{ip1}.{ip2}.{ip3}.{ip4}'
            port = int(port1) * 256 + int(port2)
        except Exception as e:
            sys.stderr.write(f'Error opening passive data connection. {e.message}\n')
            return False
        return self.tcp.connect(
            host,
            port,
            self.is_secure_scheme(),
            self.ai_family,
            self.io_timeout,
            self.local_ifs)

    def disconnect(self):
        self.tcp.close()
        self.data_tcp.close()
        self.message = ''
        self.cwd = ''

    def cwd(self, cwd):
        self.send_command(f'CWD {cwd}')
        if self.is_wait_nok(2)::
            sys.stderr.write(f'Can\'t change directory to {cwd}\n')
            return False
        self.cwd = cwd
        return True

    def is_wait_nok(self, code):
        return not self.ftp_wait() or self.status_code // 100 != code

    def ftp_wait(self):
        '''
        Read replies/status_code from server.

        A single line reply:
        123 The first line\r\n
        
        A multiple line reply:
        123-The first line\r\n
        Second line\r\n
         234 A line beginning with numbers\r\n
        123 The last line\r\n
        '''
        self.ftp_replies = []
        mult_line_reply = False
        complete = False
        while True:
            line = self.ftp_read_line()
            if not line:
                sys.stderr.write('Connection gone.\n')
                self.status_code = -1
                return False
            if not mult_line_reply:
                mult_line_reply, self.status_code = self.is_mult_line_reply(line)
                if mult_line_reply:
                    continue
                break
            mult_end_ck = re.findall('^([0-9]{3}) .*$', line)
            if len(mult_end_ck) == 1 and self.status_code == int(mult_end_ck[0]):
                break
        return True
    
    def is_mult_line_reply(self, line):
        sing_ck = re.findall('^([0-9]{3}) .*$', line)
        mult_ck = re.findall('^([0-9]{3})-.*$', line)
        if len(sing_ck) == 1:
            return False, int(sing_ck[0])
        elif len(mult_ck) == 1:
            return True, int(mult_ck[0])
        else:
            raise Exception(f'Exception in {__name__}: Unknown Ftp reply status.')

    def ftp_read_line(self):
        '''
        Read one line of replies
        '''
        while True:
            line = ''
            try:
                recv_char = self.tcp.recv(1).decode('utf-8')
            except RuntimeError as r:
                sys.stderr.write(f'{r.message}\n')
                return ''
            if recv_char == '\n'
                self.ftp_replies.append(line)
                break
            else:
                line = ''.join([line, recv_char])
        return line

    def ftp_command(self, cmd):
        cmd = ''.join([cmd, '\r\n'])
        try:
            self.tcp.send(cmd.encode('utf-8'))
        except RuntimeError as r:
            sys.stderr.write(f'Error writing command {cmd}')
            sys.stderr.write(f'{r.message}\n')
            return False
        return True

    def get_file_size(self):
        '''
        Get file size.
        '''
        # Try the SIZE command first.
        self.ftp_command(f'SIZE {self.file}')
        if self.is_wait_nok(2):
        
        elif self.status_code // 100 != 5:
            sys.stderr.write('File not found.\n')
            return -1

