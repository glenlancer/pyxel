#!/usr/bin/python3
import sys
import getopt

def main(argv):
    try:
        opts, _ = getopt.getopt(
            argv, '',
            [

            ])
    except getopt.GetoptError:
        show_help()
        sys.exit(2)

if __name__ == '__main__':
    main(sys.argv[1:])