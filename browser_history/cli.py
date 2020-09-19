"""This module defines functions and globals required for the
command line interface of browser-history."""

import sys
import argparse
from browser_history import generic, browsers, utils

# get list of all implemented browser by finding subclasses of generic.Browser
AVAILABLE_BROWSERS = ', '.join(b.__name__ for b in generic.Browser.__subclasses__())

def make_parser():
    """Creates an ArgumentParser, configures and returns it.

    This was made into a separate function to be used with sphinx-argparse

    :rtype: :py:class:`argparse.ArgumentParser`
    """
    parser_ = argparse.ArgumentParser(description='''
                                            A tool to retrieve history from
                                            (almost) any browser on (almost) any platform''',
                                         epilog='''
                                            Checkout the GitHub repo https://github.com/pesos/browser-history
                                            if you have any issues or want to help contribute''')

    parser_.add_argument('-b', '--browser',
                            default='all',
                            help=f'''
                                browser to retrieve history from. Should be one of all, {AVAILABLE_BROWSERS}.
                                Default is all (gets history from all browsers).''')
    return parser_

parser = make_parser()

def main():
    """Entrypoint to the command-line interface (CLI) of browser-history.

    It parses arguments from sys.argv and performs the appropriate actions.
    """
    args = parser.parse_args()

    if args.browser == 'all':
        outputs = utils.get_history()

    else:
        try:
            # gets browser class by name (string). TODO: make it case-insensitive
            selected_browser = args.browser
            for browser in generic.Browser.__subclasses__():
                if browser.__name__.lower() == args.browser.lower():
                    selected_browser = browser.__name__
                    break
            browser_class = getattr(browsers, selected_browser)
        except AttributeError:
            print(f'Browser {args.browser} is unavailable. Check --help for available browsers')
            sys.exit(1)

        try:
            browser = browser_class().fetch()
            outputs = browser
        except AssertionError as e:
            print(e)
            sys.exit(1)

    for date, url in outputs.get():
        # comma-separated output. NOT a CSV file
        print(f'{date},{url}')
