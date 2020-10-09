"""This module defines functions and globals required for the
command line interface of browser-history."""

import sys
import argparse
from browser_history import get_history, generic, browsers,get_bookmarks

# get list of all implemented browser by finding subclasses of generic.Browser
AVAILABLE_BROWSERS = ', '.join(b.__name__ for b in generic.Browser.__subclasses__())
AVAILABLE_FORMATS = ', '.join(generic.Outputs.formats)
AVAILABLE_TYPES='history,bookmarks'

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

    parser_.add_argument('-t','--type',
                        default='all',
                        help=f'''
                                argument to decide whether to retrieve history or bookmarks.
                                Should be one of all, {AVAILABLE_TYPES}.
                                Default is all (gets both histories and bookmarks)
                                .''')
    parser_.add_argument('-b', '--browser',
                         default='all',
                         help=f'''
                                browser to retrieve history or bookmarks from. Should be one of all, {AVAILABLE_BROWSERS}.
                                Default is all (gets history or bookmarks from all browsers).''')

    parser_.add_argument('-f', '--format',
                         default="csv",
                         help=f'''
                                Format to be used in output. Should be one of {AVAILABLE_FORMATS}.
                                Default is csv''')

    parser_.add_argument('--history_output',
                         default=None,
                         help='''
                                File where history output is to be written. 
                                If not provided and type is history or all 
                                ,standard output is used.''')
    parser_.add_argument('--bookmarks_output',
                         default=None,
                         help='''
                                File where bookmarks output is to be written. 
                                If not provided and type is bookmarks or all
                                ,standard output is used.''')
    return parser_

parser = make_parser()    

def main():
    """Entrypoint to the command-line interface (CLI) of browser-history.

    It parses arguments from sys.argv and performs the appropriate actions.
    """
    args = parser.parse_args()
    assert args.type in ['history','bookmarks','all'], f"Type should be one of all, {AVAILABLE_TYPES}"
    if args.browser == 'all':
        if args.type == 'history':
            h_outputs = get_history()
        elif args.type == 'bookmarks':
            b_outputs = get_bookmarks()
        elif args.type == 'all':
            h_outputs = get_history()
            b_outputs = get_bookmarks()
    else:
        try:
            # gets browser class by name (string).
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
            if args.type == 'history':
                browser = browser_class().fetch(type = args.type)
                h_outputs = browser
            elif args.type == 'bookmarks':
                browser = browser_class().fetch(type = args.type)
                b_outputs = browser
            elif args.type == 'all':
                browser = browser_class().fetch(type = 'history')
                h_outputs = browser
                browser = browser_class().fetch(type = 'bookmarks')              
                b_outputs = browser
        except AssertionError as e:
            print(e)
            sys.exit(1)

    # Format the output
    try:
        if args.type == 'all':
            h_formatted = h_outputs.formatted(args.format,'history')
            b_formatted = b_outputs.formatted(args.format,'bookmarks')
        elif args.type == 'history':
            h_formatted = h_outputs.formatted(args.format,args.type)
        elif args.type == 'bookmarks':
            b_formatted = b_outputs.formatted(args.format,args.type)
    except ValueError as e:
        print(e)
        sys.exit(1)
    
    if args.history_output is None and args.type in ['history','all']:
        print(h_formatted)
    if args.bookmarks_output is None and args.type in ['bookmarks','all']:
        print(b_formatted)
    if (not args.history_output is None) and args.type in ['history','all']:
        filename = args.history_output
        with open(filename, 'w') as output_file:
            output_file.write(h_formatted)
    elif (not args.bookmarks_output is None) and args.type in ['bookmarks','all']:
        filename = args.bookmarks_output
        with open(filename, 'w') as output_file:
            output_file.write(b_formatted)
