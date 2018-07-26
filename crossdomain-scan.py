#!/usr/bin/env python
'''
A toy/PoC scanner of crossdomain.xml for expired domains.
'''

import os
import sys
import random
import argparse
import logging

from crossdomain import CrossDomainScanner


class ConsoleLogFormatter(logging.Formatter):

    @property
    def pretty_levels(self):
        BOLD = "\033[1m"
        RESET = "\033[0m"
        return {
            'INFO': BOLD + "\033[36m[*]" + RESET,
            'WARNING': BOLD + "\033[33m[!]" + RESET,
            'DEBUG': BOLD + "\033[34m[-]" + RESET,
            'ERROR': BOLD + "\033[31m[X]" + RESET,
            'CRITICAL': BOLD + "\033[32m[$]" + RESET,
        }

    def format(self, record):
        level = self.pretty_levels.get(record.levelname, "")
        return "%s %s " % (
            level, record.msg,
        )


class ConsoleLogHandler(logging.Handler):

    def emit(self, record):
        msg = self.format(record)
        sys.stdout.write(chr(27) + '[2K\r')
        if record.levelname == 'INFO':
            sys.stdout.write(msg)
            sys.stdout.flush()
        else:
            print msg


def read_files(files):
    ''' Simple helper function '''
    domains = []
    for f in files:
        if os.path.exists(f) and os.path.isfile(f):
            with open(f, 'r') as fp:
                domains += [
                    line.split(',')[1].strip() for line in fp.readlines()
                ]
        else:
            print "Error: File does not exist:", f
    return domains

def read_input(file):
    ''' Simple helper function '''
    domains = []
    if os.path.exists(file) and os.path.isfile(file):
        with open(file, 'r') as fp:
            domains += [
                line.strip() for line in fp.readlines()
            ]
    else:
        print "Error: File does not exist:", file
    return domains


def get_domains(args):
    _domains = []
    if args.files:
        _domains += read_files(args.files)
    if args.domains:
        _domains += args.domains
    if args.randomize:
        random.shuffle(_domains)
    if args.input:
        _domains += read_input(args.input)
    return _domains


def display_results(results, wildcards, outfile):
    f = open(outfile,'w')
    sys.stdout.write(chr(27) + '[2K\r\n')
    if (len(results) != 0) or (len(wildcards) != 0):
        # save the results to a file
        print "%d crossdomain.xml(s) with wildcards" % len(wildcards)
        for index, domain in enumerate(wildcards):
            print "\t%d. %s" % (index + 1, domain)
            f.write("%s,wildcard,*\n" % (domain))
        print "%d crossdomain.xml(s) with expired domains" % len(results)
        for index, domain in enumerate(results):
            print "\t%d. %s: %s" % (index + 1, domain, ", ".join(results[domain]))
            f.write("%s,expired,%s\n" % (domain, ", ".join(results[domain])))
        f.close()
    else: 
        # save empty results to a file
        f.write('NA')
        f.close()


def _main(args):
    scanner = CrossDomainScanner(get_domains(args),
                                 http_timeout=args.http_timeout)
    try:
        logger = logging.getLogger('CrossDomain')
        logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
        console = ConsoleLogHandler()
        console.setFormatter(ConsoleLogFormatter())
        logger.addHandler(console)
        tld_logger = logging.getLogger("tldextract")
        tld_logger.addHandler(logging.NullHandler())
        scanner.start()
    except KeyboardInterrupt:
        sys.stdout.write(chr(27) + '[2K\r')
        print "User exit."
    finally:
        display_results(scanner.results, scanner.wildcards, args.output)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Check crossdomain.xml files for expired domains.',
    )
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s v0.0.1'
                        )
    parser.add_argument('--domains', '-d',
                        help='domains to check',
                        dest='domains',
                        nargs='*',
                        )
    parser.add_argument('--alexa', '-a',
                        help='read domains from alexa formatted csv file(s)',
                        dest='files',
                        nargs='*',
                        )
    parser.add_argument('--randomize-hosts', '-r',
                        help='Randomize the order in which hosts are scanned',
                        dest='randomize',
                        action='store_true',
                        )
    parser.add_argument('--output', '-o',
                        help='Output file to store the results',
                        dest='output',
                        action='store',
                        )
    parser.add_argument('--http-timeout', '-t',
                        help='HTTP request timeout',
                        dest='http_timeout',
                        default=3,
                        )
    parser.add_argument('--verbose', '-V',
                        help='Verbose output to logs/console',
                        dest='verbose',
                        action='store_true',
                        )
    parser.add_argument('--input', '-iL',
                        help='input file containing domains',
                        dest='input',
                        action='store',
                        )
    _main(parser.parse_args())
