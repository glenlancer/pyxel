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
    print('--ipv6\t\t\t-6\tUse the IPv6 protocol')
    print('--header=x\t\t\t-H x\tAdd HTTP header string')
    print('--user-agent=x\t\t-U x\tSet user agent')
    print('--no-proxy\t\t-N\tJust don\'t use any proxy server')
    print('--insecure\t\t-k\tDon\'t verify the SSL certificate')
    print('--no-clobber\t\t-c\tSkip download if file already exists')
    print('--quiet\t\t\t-q\tLeave stdout alone')
    print('--verbose\t\t-v\tMore status information')
    print('--alternate\t\t-a\tAlternate progress indicator')
    print('--timeout=x\t\t-T x\tSet I/O and connection timeout')
    print('--help\t\t\t-h\tShow this information')
    print('--version\t\t-v\tVerson information')

def initializing_tasks(config):
    for url in config.urls:
        print(f'Initializing download: {url}')
        # Handle do_search here?
        
    print()
    pass

def command_process(argv, config):
    try:
        opts, args = getopt.getopt(
            argv, 'hVs:n:o:S:46H:Nv',
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
                'verbose',
            ])
    except getopt.GetoptError:
        print_help()
        return []
    if not opts:
        print_help()
        return []
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
        elif opt in ('-v', '--verbose'):
            if arg.lower() == 'true':
                config.verbose = True
            else:
                config.verbose = False
                config.alternate_output = False
        elif opt in ('-h', '--help'):
            print_help()
            return []
        elif opt in ('-V', '--version'):
            print_version()
            return []
    return args

def main(argv):
    config = Config()
    urls = command_process(argv, config):
    if urls:
        config.urls = urls
        initializing_tasks(config)
    else:
        print('There is no url provided.')
        print_help()

if __name__ == '__main__':
    main(sys.argv[1:])