"""Command line interface of browser-history."""

import argparse
import sys
from argparse import RawDescriptionHelpFormatter
from typing import List, Optional

from browser_history import __version__, get_bookmarks, get_history, outputs, utils

# get list of all implemented browser by finding subclasses of generic.Browser
AVAILABLE_BROWSERS = ", ".join(b.__name__ for b in utils.get_browsers())
AVAILABLE_FORMATS = ", ".join(outputs.Outputs._format_map.keys())
AVAILABLE_TYPES = ", ".join(
    sub._fetch_type() for sub in outputs.Outputs.__subclasses__()
)


def make_parser() -> argparse.ArgumentParser:
    """Create an :py:class:`argparse.ArgumentParser`, configures and returns it.

    This was made into a separate function to be used with sphinx-argparse.
    """
    parser_ = argparse.ArgumentParser(
        description="""
                    A tool to retrieve history from
                    (almost) any browser on (almost) any platform

██████╗ ██████╗  ██████╗ ██╗    ██╗███████╗███████╗██████╗       ██╗  ██╗██╗███████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔════╝██╔════╝██╔══██╗      ██║  ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
██████╔╝██████╔╝██║   ██║██║ █╗ ██║███████╗█████╗  ██████╔╝█████╗███████║██║███████╗   ██║   ██║   ██║██████╔╝ ╚████╔╝
██╔══██╗██╔══██╗██║   ██║██║███╗██║╚════██║██╔══╝  ██╔══██╗╚════╝██╔══██║██║╚════██║   ██║   ██║   ██║██╔══██╗  ╚██╔╝
██████╔╝██║  ██║╚██████╔╝╚███╔███╔╝███████║███████╗██║  ██║      ██║  ██║██║███████║   ██║   ╚██████╔╝██║  ██║   ██║
╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝      ╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝
                    """,  # noqa: E501
        # TODO: fix indentation for all of these using inspect.cleandoc
        epilog="""
                Checkout the GitHub repo
                https://github.com/browser-history/browser-history
                if you have any issues or want to help contribute.""",
        formatter_class=RawDescriptionHelpFormatter,
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
        default=None,
        help=f"""
            Format to be used in output. Should be one of {AVAILABLE_FORMATS}.
            If not specified, format is inferred from the output file's
            extension. If no output file (-o) is specified, it defaults to csv.""",
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
                not provided all profiles are fetched.
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


def cli(raw_args: List[str]):
    """Entrypoint to the command-line interface (CLI) of browser-history."""
    args = parser.parse_args(raw_args)
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
        for profile in browser_class()._profiles(browser_class._history_file):
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
        profile: Optional[str] = args.profile
        profiles = []
        if profile is not None:
            if not browser_class.profile_support:
                utils.logger.critical(
                    "%s browser does not support profiles", browser.name
                )
                sys.exit(1)

            # get the actual path from profile name
            if args.type == "history":
                profile_path = browser._history_paths(profile)
            elif args.type == "bookmarks":
                profile_path = browser._bookmark_paths(profile)
            else:
                # TODO: can this ever occur?
                raise Exception(f"Unrecognized type: {args.type}")

            if not profile_path.exists():
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
                profiles = [profile_path]

        if args.type == "history":
            outputs = browser.fetch_history(profiles)
        elif args.type == "bookmarks":
            outputs = browser.fetch_bookmarks(profiles)
        else:
            # TODO: can this ever occur?
            raise Exception(f"Unrecognized type: {args.type}")

    try:
        if args.output is None:
            if args.format is None:
                args.format = "csv"
            print(outputs.formatted(args.format))
        elif args.output is not None:
            outputs.save(args.output, args.format)

    except ValueError as e:
        utils.logger.error(e)
        sys.exit(1)


def main():
    """Entrypoint to the command-line interface (CLI) of browser-history.

    Takes parameters from `sys.argv`.
    """
    cli(sys.argv[1:])
