import sys
import argparse
from browser_history import generic, browsers, utils

# get list of all implemented browser by finding subclasses of generic.Browser
available_browsers = ', '.join(b.__name__ for b in generic.Browser.__subclasses__())

parser = argparse.ArgumentParser(description='''
                                    A tool to retrieve history from
                                    (almost) any browser on (almost) any platform''',
                                 epilog='''
                                    Checkout the GitHub repo https://github.com/pesos/browser-history
                                    if you have any issues or want to help contribute''')

parser.add_argument('-b', '--browser',
                    default='all',
                    help=f'''
                        browser to retrieve history from. Should be one of all, {available_browsers}.
                        Default is all (gets history from all browsers).''')

def main():
    args = parser.parse_args()

    if args.browser == 'all':
        outputs = utils.get_history()

    else:
        try:
            # gets browser class by name (string). TODO: make it case-insensitive
            browser_class = getattr(browsers, args.browser)
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
