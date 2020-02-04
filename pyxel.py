#!/usr/bin/python3
import sys
import getopt
import re
from functions.config import Config

def is_filename_valid(file_name):
    ''' check if given filename is valid '''
    chars = '^[\-_\.a-zA-Z0-9]*$'
    return re.match(chars, file_name)

def print_version():
    print('Pyxel version 1.0')

def print_help():
    print('Usage: pyxel [options] url1 [url2] [url...]')
    print()
    print('--max-speed=x\t\t-s x\tSpecifiy maximum speed (bytes per second)')
    print('--num-connections=x\t-n x\tSpecify maximum number of connections')
    print('--max-redirect=x\t\tSpecify maximum number of redirections')
    print('--output=f\t\t-o f\tSpecify local output file')
    print('--search=n\t\t-S n\tSearch for mirrors and download from n servers')
    print('--ipv4\t\t\t-4\tUse the IPv4 protocol')
    print('--help\t\t\t-h\tShow this information')
    print('--version\t\t-v\tVerson information')

""
		 "--ipv6\t\t\t-6\tUse the IPv6 protocol\n"
		 "--header=x\t\t-H x\tAdd HTTP header string\n"
		 "--user-agent=x\t\t-U x\tSet user agent\n"
		 "--no-proxy\t\t-N\tJust don't use any proxy server\n"
		 "--insecure\t\t-k\tDon't verify the SSL certificate\n"
		 "--no-clobber\t\t-c\tSkip download if file already exists\n"
		 "--quiet\t\t\t-q\tLeave stdout alone\n"
		 "--verbose\t\t-v\tMore status information\n"
		 "--alternate\t\t-a\tAlternate progress indicator\n"
		 "--help\t\t\t-h\tThis information\n"
		 "--timeout=x\t\t-T x\tSet I/O and connection timeout\n"

def initializing_task(config):
    pass

def command_process(argv, config):
    try:
        opts, _ = getopt.getopt(
            argv, 'hvs:n:o:S:46H:N',
            [
                'help',
                'version',
                'max-speed=',
                'num-connections=',
                'max-redirect=',
                'output=',
                'search=',
                'ipv4',
                'ipv6',
                'header=',
                'no-proxy',

            ])
    except getopt.GetoptError:
        show_help()
        return False
    if not opts:
        print_help()
        return False
    for opt, arg in opts:
        if opt in ('-s', '--max-speed'):
            config.max_speed = int(arg)
        elif opt in ('-n', '--num-connections'):
            config.num_of_connections = int(arg)
        elif opt in ('-s', '--max-redirect'):
            config.max_redirect = int(arg)
        elif opt in ('-o', '--output'):
            if is_filename_valid(arg):
                config.output = arg
            else:
                raise Exception(f'Exception in {__name__}: invalid file name.')
        elif opt in ('-S', '--search'):
            config.do_search = True
            config.search_top = int(arg)
        elif opt in ('-4', '--ipv4'):
            config.set_protocol('ipv4')
        elif opt in ('-6', '--ipv6'):
            config.set_protocol('ipv6')
        elif opt in ('-H', '--header'):
            header, value = arg.split(':')
            config.add_header(
                header.strip(), value.strip()
            )
        elif opt in ('-N', '--no-proxy'):
            config.http_proxy = ''
        elif opt in ('-h', '--help'):
            print_help()
            return False
        elif opt in ('-v', '--version'):
            print_version()
            return False
    return True

def main(argv):
    config = Config()
    if command_process(argv, config):
        initializing_task(config)

if __name__ == '__main__':
    main(sys.argv[1:])