#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
import getopt
import re
from functions.config import Config
from functions.config import is_filename_valid
from functions.tasker import Tasker

def print_version():
    print('Pyxel version 1.0')
    print('Author: Glen Lin')
    print('Email: glenlancer@163.com')

def print_help():
    print('Usage: pyxel [options] url1 [url2] [url...]')
    print()
    print('--max-speed=x\t\t-s x\tSpecifiy maximum speed (bytes per second)')
    print('--num-connections=x\t-n x\tSpecify maximum number of connections')
    print('--max-redirect=x\t\tSpecify maximum number of redirections')
    print('--output=f\t\t-o f\tSpecify local output file')
    print('--ipv4\t\t\t-4\tUse the IPv4 protocol')
    print('--ipv6\t\t\t-6\tUse the IPv6 protocol')
    print('--header=x\t\t\t-H x\tAdd HTTP header string')
    print('--user-agent=x\t\t-U x\tSet user agent')
    print('--no-proxy\t\t-N\tJust don\'t use any proxy server')
    print('--insecure\t\t-k\tDon\'t verify the SSL certificate')
    print('--no-clobber\t\t-c\tSkip download if file already exists')
    print('--quiet\t\t\t-q\tLeave stdout alone')
    print('--verbose\t\t-V\tMore status information')
    print('--alternate\t\t-a\tAlternate progress indicator')
    print('--timeout=x\t\t-T x\tSet I/O and connection timeout')
    print('--help\t\t\t-h\tShow this information')
    print('--version\t\t-v\tVerson information')

def command_process(argv, config):
    try:
        opts, args = getopt.getopt(
            argv, 'hvs:n:o:46H:U:NkcqVaT:',
            [
                'help',
                'version',
                'max-speed=',
                'num-connections=',
                'max-redirect=',
                'output=',
                'ipv4',
                'ipv6',
                'header=',
                'user-agent=',
                'no-proxy',
                'insecure',
                'no-clobber',
                'quiet',
                'verbose',
                'alternate',
                'timeout=',
            ])
    except getopt.GetoptError:
        print_help()
        return False, None
    for opt, arg in opts:
        if opt in ('-s', '--max-speed'):
            config.max_speed = int(arg)
        elif opt in ('-n', '--num-connections'):
            config.num_of_connections = int(arg)
        elif opt in ('-s', '--max-redirect'):
            config.max_redirect = int(arg)
        elif opt in ('-o', '--output'):
            if is_filename_valid(arg):
                config.output_filename_from_cmd = arg
            else:
                raise Exception(f'Exception in {__name__}: invalid file name. {arg}')
        elif opt in ('-4', '--ipv4'):
            config.set_protocol('ipv4')
        elif opt in ('-6', '--ipv6'):
            config.set_protocol('ipv6')
        elif opt in ('-H', '--header'):
            header, value = arg.split(':')
            config.set_header(
                header, value
            )
        elif opt in ('-U', '--user-agent'):
            config.set_header(
                'User-Agent', arg
            )
        elif opt in ('-N', '--no-proxy'):
            config.http_proxy = None
        elif opt in ('-k', '--insecure'):
            config.insecure = True
        elif opt in ('-c', '--no-clobber'):
            config.no_clobber = True
        elif opt in ('-q', '--quiet'):
            config.standard_output = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            config.verbose = False
        elif opt in ('-V', '--verbose'):
            if arg.lower() == 'true':
                config.verbose = True
            else:
                config.verbose = False
                config.alternate_output = False
        elif opt in ('-a', '--alternate'):
            config.alternate_output = True
        elif opt in ('-T', '--timeout'):
            config.io_timeout = int(arg)
        elif opt in ('-h', '--help'):
            print_help()
            return True, None
        elif opt in ('-v', '--version'):
            print_version()
            return True, None
    if len(args) < 1:
        print_help()
        return False, None
    else:
        return True, args[0]

def main(argv):
    config = Config()
    ok, url = command_process(argv, config)
    if ok and url is not None:
        tasker = Tasker(config, url)
        tasker.start_task()
    elif not ok:
        print('\nThere is no url provided.')

if __name__ == '__main__':
    main(sys.argv[1:])