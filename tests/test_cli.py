import csv
import itertools
import json
import tempfile

import pytest

from browser_history import get_browsers
from browser_history.cli import cli, AVAILABLE_BROWSERS
from .utils import (  # noqa: F401
    become_linux,
    become_mac,
    become_windows,
    change_homedir,
)

# pylint: disable=redefined-outer-name,unused-argument

CMD_ROOT = "browser-history"

# Options:
VALID_CMD_OPTS = [
    (f"--{long_o}", f"-{short_o}")
    for long_o, short_o in [
        ("help", "h"),
        ("type", "t"),
        ("browser", "b"),
        ("format", "f"),
        ("output", "o"),
    ]
]
INVALID_CMD_OPTS = [
    "--history",
    "-a",
    "-B",
    "-0",
]

# Arguments, where the default arg should be put first for default testing:
VALID_TYPE_ARGS = [
    "history",
    "bookmarks",
]
INVALID_TYPE_ARGS = ["cookies", "lol", "histories", "bookmark"]
VALID_BROWSER_ARGS = [
    "all",
    "Chrome",
    "Chromium",
    "Firefox",
    "Safari",
    "Edge",
    "Opera",
    "OperaGX",
    "Brave",
]
INVALID_BROWSER_ARGS = ["explorer", "ie", "netscape", "none", "brr"]
VALID_FORMAT_ARGS = [
    "infer",
    "csv",
    "json",
    "jsonl",
]
INVALID_FORMAT_ARGS = ["csvv", "txt", "html", "qwerty"]
# (VALID_OUTPUT_ARGS is any existent file, so validity depends on the fs)
GENERAL_INVALID_ARGS = [
    "foo",
    "0",
]

# Output markers:
HELP_SIGNATURE = (
    "usage: browser-history " "[-h] [-t TYPE] [-b BROWSER] [-f FORMAT] [-o OUTPUT]"
)
HISTORY_HEADER = "Timestamp,URL"
BOOKMARKS_HEADER = "Timestamp,URL,Title,Folder"

CSV_HISTORY_HEADER = HISTORY_HEADER
CSV_BOOKMARKS_HEADER = BOOKMARKS_HEADER


platform_fixture_map = {
    "linux": become_linux,
    "windows": become_windows,
    "mac": become_mac,
}
all_platform_fixtures = tuple("become_" + plat for plat in platform_fixture_map.keys())


@pytest.fixture
def platform(request):
    """Fixture to change platform based on pytest parameter"""
    request.getfixturevalue("change_homedir")
    return request.getfixturevalue(request.param)


def _get_browser_available_on_system():
    """Find a browser that is supported and installed on the test system."""
    for browser in get_browsers():
        try:  # filter out unsupported browsers
            history = browser().fetch_history()
        except AssertionError:  # anything caught here is unsupported
            continue
        # Has non-empty history so must be installed as well as supported
        if json.loads(history.to_json())["history"]:
            # Return string name which corresponds to a VALID_BROWSER_ARGS entry
            return browser.name
    return  # None indicating no browsers available on system


@pytest.mark.parametrize("platform", all_platform_fixtures, indirect=True)
def test_no_argument(capsys, platform):
    """Test the root command gives basic output."""
    cli([])
    captured = capsys.readouterr()
    assert CSV_HISTORY_HEADER in captured.out


@pytest.mark.parametrize("platform", all_platform_fixtures, indirect=True)
def test_type_argument(capsys, platform):
    """Test arguments for the type option."""
    for type_opt in VALID_CMD_OPTS[1]:
        for type_arg in VALID_TYPE_ARGS:
            cli([type_opt, type_arg])
            captured = capsys.readouterr()
            if type_arg == "history":
                # assuming csv is default
                assert captured.out.startswith(CSV_HISTORY_HEADER)
            if type_arg == "bookmarks":
                assert captured.out.startswith(CSV_BOOKMARKS_HEADER)


@pytest.mark.parametrize("browser_arg", VALID_BROWSER_ARGS)
@pytest.mark.parametrize("platform", all_platform_fixtures, indirect=True)
def test_browser_argument(browser_arg, capsys, platform):
    """Test arguments for the browser option."""
    for browser_opt in VALID_CMD_OPTS[2]:
        try:
            cli([browser_opt, browser_arg])
            captured = capsys.readouterr()
            assert CSV_HISTORY_HEADER in captured.out
        except AssertionError as e:
            if any(
                browser_unavailable_err in e.args[0]
                for browser_unavailable_err in (
                    "browser is not supported",
                    "browser is not installed",
                )
            ):
                # In case the tester does not have access to the browser
                # in question, which makes the command fail, but in a way
                # that is expected and gives a recognised error message.
                pytest.skip(
                    "Unable to test against {} browser because it is "
                    "not available locally".format(browser_opt)
                )
            else:  # command fails for another reason i.e. a test failure
                pytest.fail(
                    "{} browser is available but the command to fetch "
                    "the history from it has failed.".format(browser_opt)
                )


@pytest.mark.parametrize("platform", all_platform_fixtures, indirect=True)
def test_format_argument(capsys, platform):
    """Tests arguments for the format option."""
    # First check format of default:
    cli([])
    captured = capsys.readouterr()
    csv_output = captured.out
    # Sniffer determines format, less intensive than reading in csv.reader
    # and we don't mind the CSV dialect, so just check call doesn't error
    read_csv = csv.Sniffer()
    # This gives '_csv.Error: Could not determine delimiter' if not a csv file
    read_csv.sniff(csv_output, delimiters=",")
    assert read_csv.has_header(
        csv_output
    ), "CSV format missing heading with type followed by column names."

    for fmt_opt in VALID_CMD_OPTS[3]:
        for fmt_arg in VALID_FORMAT_ARGS:
            cli([fmt_opt, fmt_arg])
            output = capsys.readouterr().out
            if fmt_arg in ("csv", "infer"):  # infer gives csv if no file
                read_csv.sniff(output, delimiters=",")
                assert read_csv.has_header(output)
                assert CSV_HISTORY_HEADER in output
            elif fmt_arg == "json":
                json.loads(output)
            elif fmt_arg == "jsonl":
                # Newline-delimited json so test each line is valid json
                for line in output.splitlines():
                    json.loads(line)


@pytest.mark.parametrize("platform", all_platform_fixtures, indirect=True)
def test_output_argument(capsys, platform):
    """Test arguments for the output option."""
    for output_opt in VALID_CMD_OPTS[4]:
        with tempfile.TemporaryDirectory() as tmpdir:
            cli([output_opt, tmpdir + "out.csv"])
            output = capsys.readouterr().out
            # Check output was not sent to STDOUT since should go to file
            assert HISTORY_HEADER not in output
            with open(tmpdir + "out.csv", "rt") as f:  # now check the file
                assert HISTORY_HEADER in f.read()


@pytest.mark.parametrize("platform", all_platform_fixtures, indirect=True)
@pytest.mark.parametrize("browser", AVAILABLE_BROWSERS.split(", "))
def test_argument_combinations(capsys, platform, browser):
    """Test that combinations of optional arguments work properly."""
    # Choose some representative combinations. No need to test every one.
    indices = (0, 1)
    available_browser = _get_browser_available_on_system()
    # To test combos of short or long option variants
    for index_a, index_b in itertools.product(indices, indices):
        if available_browser:
            try:
                cli(
                    [
                        VALID_CMD_OPTS[1][index_a],  # type
                        VALID_TYPE_ARGS[1],  # ... is bookmarks,
                        VALID_CMD_OPTS[2][index_a],  # browser
                        browser,  # ... is any usable on system
                    ]
                )
            except AssertionError as e:
                if any(
                    browser_unavailable_err in e.args[0]
                    for browser_unavailable_err in (
                        "browser is not supported",
                        "browser is not installed",
                        "Bookmarks are not supported",
                    )
                ):
                    # In case the tester does not have access to the browser
                    # in question, which makes the command fail, but in a way
                    # that is expected and gives a recognised error message.
                    pytest.skip(
                        "Unable to test against {} browser because it is "
                        "not available locally".format(browser)
                    )
                else:  # command fails for another reason i.e. a test failure
                    pytest.fail(
                        "{} browser is available but the command to fetch "
                        "the history from it has failed.".format(browser)
                    )
            output = capsys.readouterr().out

            read_csv = csv.Sniffer()
            read_csv.sniff(output, delimiters=",")
            assert read_csv.has_header(output)
        else:  # unlikely but catch just in case can't use any browser
            for _ in range(3):  # to cover all three assert tests above
                pytest.skip("No browsers available to test with")
        with tempfile.TemporaryDirectory() as tmpdir:
            # This command should write to the given output file:
            cli(
                [
                    VALID_CMD_OPTS[3][index_b],  # format
                    VALID_FORMAT_ARGS[2],  # ... is json,
                    VALID_CMD_OPTS[4][index_b],  # output
                    tmpdir + "out.json",  # ... is a named file
                ]
            )
            with open(tmpdir + "out.json", "rb") as f:
                json.loads(f.read().decode("utf-8"))


def test_help_option(capsys):
    """Test the command-line help provided to the user on request."""
    for help_opt in VALID_CMD_OPTS[0]:
        with pytest.raises(SystemExit) as e:
            cli([help_opt])
            output = capsys.readouterr()
            assert HELP_SIGNATURE in output
            assert e.value.code == 0


def test_invalid_options(change_homedir):  # noqa: F811
    """Test that invalid options error correctly."""
    for bad_opt in INVALID_CMD_OPTS:
        with pytest.raises(SystemExit) as e:
            cli([bad_opt])
            assert e.value.code == 2


def test_invalid_format(change_homedir):  # noqa: F811
    """Test that invalid formats error correctly."""
    for bad_format in INVALID_FORMAT_ARGS:
        with pytest.raises(SystemExit) as e:
            cli(["-f", bad_format])
            assert e.value.code == 1


def test_invalid_type(change_homedir):  # noqa: F811
    """Test that invalid types error correctly."""
    for bad_type in INVALID_TYPE_ARGS:
        with pytest.raises(SystemExit) as e:
            cli(["-t", bad_type])
            assert e.value.code == 1


def test_invalid_browser(change_homedir):  # noqa: F811
    """Test that invalid browsers error correctly."""
    for bad_browser in INVALID_BROWSER_ARGS:
        with pytest.raises(SystemExit) as e:
            cli(["-b", bad_browser])
            assert e.value.code == 1
