"""This module defines functions and globals required for the
command line interface of browser-history."""

import sys
import argparse
from browser_history import get_history, get_bookmarks, generic, browsers, utils

# get list of all implemented browser by finding subclasses of generic.Browser
AVAILABLE_BROWSERS = ", ".join(b.__name__ for b in generic.Browser.__subclasses__())
AVAILABLE_FORMATS = ", ".join(generic.Outputs(fetch_type=None).format_map.keys())
AVAILABLE_TYPES = ", ".join(generic.Outputs(fetch_type=None).field_map.keys())


def make_parser():
    """Creates an ArgumentParser, configures and returns it.

    This was made into a separate function to be used with sphinx-argparse

    :rtype: :py:class:`argparse.ArgumentParser`
    """
    parser_ = argparse.ArgumentParser(
        description="""
                    A tool to retrieve history from
                    (almost) any browser on (almost) any platform""",
        epilog="""
                Checkout the GitHub repo https://github.com/pesos/browser-history
                if you have any issues or want to help contribute""",
    )

    parser_.add_argument(
        "-t",
        "--type",
        default="history",
        help=f"""
                argument to decide whether to retrieve history or bookmarks.
                Should be one of all, {AVAILABLE_TYPES}.
                Default is history.""",
    )
    parser_.add_argument(
        "-b",
        "--browser",
        default="all",
        help=f"""
                browser to retrieve history or bookmarks from. Should be one of all, {AVAILABLE_BROWSERS}.
                Default is all (gets history or bookmarks from all browsers).""",
    )

    parser_.add_argument(
        "-f",
        "--format",
        default="infer",
        help=f"""
            Format to be used in output. Should be one of {AVAILABLE_FORMATS}.
            Default is infer (it tries to infer it from the output file's extension. If no output file is given or
            if the format can't be inferred, it defaults to csv)""",
    )

    parser_.add_argument(
        "-o",
        "--output",
        default=None,
        help="""
                File where history output or bookmark output is to be written. 
                If not provided, standard output is used.""",
    )

    return parser_


parser = make_parser()


def main():
    """Entrypoint to the command-line interface (CLI) of browser-history.

    It parses arguments from sys.argv and performs the appropriate actions.
    """
    args = parser.parse_args()
    h_outputs = b_outputs = None
    fetch_map = {
        "history": {"var": h_outputs, "fun": get_history},
        "bookmarks": {"var": b_outputs, "fun": get_bookmarks},
    }

    assert (
        args.type in fetch_map.keys()
    ), f"Type should be one of all, {AVAILABLE_TYPES}"

    if args.browser == "all":
        fetch_map[args.type]["var"] = fetch_map[args.type]["fun"]()
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
            utils.logger.error('Browser %s is unavailable. Check --help for available browsers',
                               args.browser)
            sys.exit(1)

        try:
            if args.type == "history":
                fetch_map[args.type]["var"] = browser_class().fetch_history()
            elif args.type == "bookmarks":
                fetch_map[args.type]["var"] = browser_class().fetch_bookmarks()
        except AssertionError as e:
            utils.logger.error(e)
            sys.exit(1)

    try:
        if args.output is None:
            if args.format == "infer":
                args.format = "csv"
            print(args.type + ":")
            print(fetch_map[args.type]["var"].formatted(args.format))
        elif not args.output is None:
            fetch_map[args.type]["var"].save(args.output, args.format)

    except ValueError as e:
        utils.logger.error(e)
        sys.exit(1)
