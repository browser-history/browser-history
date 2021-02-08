"""This module defines functions and globals required for the
command line interface of browser-history."""

import argparse
import sys

from browser_history import (
    generic,
    get_bookmarks,
    get_history,
    utils,
    __version__,
)

# get list of all implemented browser by finding subclasses of generic.Browser
AVAILABLE_BROWSERS = ", ".join(b.__name__ for b in utils.get_browsers())
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
                Checkout the GitHub repo
                https://github.com/pesos/browser-history
                if you have any issues or want to help contribute""",
    )

    parser_.add_argument(
        "-t",
        "--type",
        default="history",
        help=f"""
                argument to decide whether to retrieve history or bookmarks.
                Should be one of {AVAILABLE_TYPES}.
                Default is history.""",
    )
    parser_.add_argument(
        "-b",
        "--browser",
        default="all",
        help=f"""
                browser to retrieve history or bookmarks from. Should be one
                of all, default, {AVAILABLE_BROWSERS}.
                Default is all (gets history or bookmarks from all browsers).
                """,
    )

    parser_.add_argument(
        "-f",
        "--format",
        default="infer",
        help=f"""
            Format to be used in output. Should be one of {AVAILABLE_FORMATS}.
            Default is infer (format is inferred from the output file's
            extension. If no output file (-o) is specified, it defaults to csv)""",
    )

    parser_.add_argument(
        "-o",
        "--output",
        default=None,
        help="""
                File where history output or bookmark output is to be written.
                If not provided, standard output is used.""",
    )

    parser_.add_argument(
        "-p",
        "--profile",
        default=None,
        help="""
                Specify the profile from which to fetch history or bookmarks. If
                not provided all profiles are fetched
        """,
    )

    parser_.add_argument(
        "--show-profiles",
        default=None,
        metavar="BROWSER",
        help=f"""
                List all available profiles for a given browser where browser
                can be one of default, {AVAILABLE_BROWSERS}. The browser
                must always be provided.
        """,
    )

    parser_.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    return parser_


parser = make_parser()


def cli(args):
    """Entrypoint to the command-line interface (CLI) of browser-history.

    It parses arguments from sys.argv and performs the appropriate actions.
    """
    args = parser.parse_args(args)
    if args.show_profiles:
        if args.show_profiles == "all":
            utils.logger.critical(
                "'all' cannot be used with --show-profiles"
                ", please specify a single browser"
            )
            sys.exit(1)
        browser_class = utils.get_browser(args.show_profiles)
        if browser_class is None:
            sys.exit(1)
        if not browser_class.profile_support:
            utils.logger.critical(
                "%s browser does not support profiles", browser_class.name
            )
            sys.exit(1)
        for profile in browser_class().profiles(browser_class.history_file):
            print(profile)
        # ignore all other options and exit
        sys.exit(0)
    outputs = None
    fetch_map = {
        "history": get_history,
        "bookmarks": get_bookmarks,
    }

    if args.type not in fetch_map:
        utils.logger.critical(
            "Type %s is unavailable." " Check --help for available types", args.type
        )
        sys.exit(1)

    if args.browser == "all" and args.profile is not None:
        # profiles are supported only for one browser at a time
        parser.error(
            "Cannot use --profile option without specifying a browser"
            " or with --browser set to 'all'"
        )

    if args.browser == "all":
        outputs = fetch_map[args.type]()
    else:
        browser_class = utils.get_browser(args.browser)
        if browser_class is None:
            sys.exit(1)

        browser = browser_class()
        profile = args.profile
        if profile is not None:
            if not browser_class.profile_support:
                utils.logger.critical(
                    "%s browser does not support profiles", browser.name
                )
                sys.exit(1)

            # get the actual path from profile name
            if args.type == "history":
                profile = browser.history_path_profile(profile)
            elif args.type == "bookmarks":
                profile = browser.bookmarks_path_profile(profile)

            if not profile.exists():
                # entire profile might be nonexistent or the specific history
                # or bookmark file might be missing
                utils.logger.critical(
                    "Profile '%s' not found in %s browser "
                    "or profile does not contain %s",
                    args.profile,
                    browser.name,
                    args.type,
                )
                sys.exit(1)
            else:
                # fetch_history and fetch_bookmarks require an array
                profile = [profile]

        if args.type == "history":
            outputs = browser.fetch_history(profile)
        elif args.type == "bookmarks":
            outputs = browser.fetch_bookmarks(profile)

    try:
        if args.output is None:
            if args.format == "infer":
                args.format = "csv"
            print(outputs.formatted(args.format))
        elif args.output is not None:
            outputs.save(args.output, args.format)

    except ValueError as e:
        utils.logger.error(e)
        sys.exit(1)


def main():
    cli(sys.argv[1:])
