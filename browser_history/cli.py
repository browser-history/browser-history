import sys
import argparse
from browser_history import generic, browsers

available_browsers = ', '.join(b.__name__ for b in generic.Browser.__subclasses__())
parser = argparse.ArgumentParser(description='''A tool to retrieve history from
                                             (almost) any browser on (almost) any platform''',
                                 epilog='''
                                    Checkout the GitHub repo https://github.com/pesos/browser-history
                                    if you have any issues or want to help contribute''')
parser.add_argument('-b', '--browser',
                    default='all',
                    help=f'''
                        browser to retrieve history from. Should be one of all, {available_browsers}.
                        Default is all (gets history from all browsers).
                    ''')

def main():
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.browser == 'all':
        # TODO: fix after #15 is merged
        raise NotImplementedError('Browser "all" is not available yet')

    else:
        try:
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
            print(f'{date},{url}')
