import csv
import itertools
import json
import subprocess
import tempfile

import pytest


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
VALID_FORMAT_ARGS = [
    "infer",
    "csv",
    "json",
    "jsonl",
]
# (VALID_OUTPUT_ARGS is any existent file, so validity depends on the fs)
GENERAL_INVALID_ARGS = [
    "foo",
    "0",
]

# Output markers:
HELP_SIGNATURE = (
    "usage: browser-history " "[-h] [-t TYPE] [-b BROWSER] [-f FORMAT] [-o OUTPUT]"
)
HISTORY_TITLE = "history:\n"
BOOKMARKS_TITLE = "bookmarks:\n"
HISTORY_HEADER = "Timestamp,URL"
BOOKMARKS_HEADER = "Timestamp,URL,Title,Folder"

CSV_HISTORY_HEADER = HISTORY_TITLE + HISTORY_HEADER
CSV_BOOKMARKS_HEADER = BOOKMARKS_TITLE + BOOKMARKS_HEADER


def test_no_argument():
    """Test the root command gives basic output."""
    output = subprocess.check_output([CMD_ROOT])
    assert CSV_HISTORY_HEADER in output.decode("utf-8")


def test_type_argument():
    """Test arguments for the type option."""
    for type_opt in VALID_CMD_OPTS[1]:
        for type_arg in VALID_TYPE_ARGS:
            output = subprocess.check_output([CMD_ROOT, type_opt, type_arg]).decode(
                "utf-8"
            )
            if type_arg == "history":  # in ('history', 'all')
                assert output.startswith(HISTORY_TITLE)
            if type_arg == "bookmarks":  # in ('bookmarks', 'all')
                assert output.startswith(BOOKMARKS_TITLE)


@pytest.mark.parametrize("browser_arg", VALID_BROWSER_ARGS)
def test_browser_argument(browser_arg):
    """Test arguments for the browser option."""
    for browser_opt in VALID_CMD_OPTS[2]:
        output = subprocess.Popen(
            [CMD_ROOT, browser_opt, browser_arg],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = output.communicate()
        if output.returncode == 0:
            assert CSV_HISTORY_HEADER in stdout.decode("utf-8")
        elif any(
            browser_unavailable_err in stderr.decode("utf-8")
            for browser_unavailable_err in (
                "browser is not supported",
                "browser is not installed",
            )
        ):
            # In case the tester does not have access to the browser
            # in question, which makes the command fail, but in a way
            # that is expected and gives a recognised error message.
            pytest.skip(
                "Unable to test against this browser because it is "
                "not available locally"
            )
        else:  # command fails for another reason i.e. a test failure
            pytest.fail(
                "The browser is available but the command to fetch "
                "the history from it has failed."
            )


def test_format_argument():
    """Tests arguments for the format option."""
    # First check format of default:
    csv_output = subprocess.check_output([CMD_ROOT]).decode("utf-8")
    # Sniffer determines format, less intensive than reading in csv.reader
    # and we don't mind the CSV dialect, so just check call doesn't error
    read_csv = csv.Sniffer()
    # This gives '_csv.Error: Could not determine delimiter' if not a csv file
    read_csv.sniff(csv_output, delimiters=",")
    assert read_csv.has_header(csv_output)

    for fmt_opt in VALID_CMD_OPTS[3]:
        for fmt_arg in VALID_FORMAT_ARGS:
            output = subprocess.check_output([CMD_ROOT, fmt_opt, fmt_arg]).decode(
                "utf-8"
            )
            if fmt_arg in ("csv", "infer"):  # infer gives csv if no file
                read_csv.sniff(output, delimiters=",")
                assert read_csv.has_header(output)
                assert CSV_HISTORY_HEADER in output
            elif fmt_arg == "json":
                assert output.startswith(HISTORY_TITLE)
                # Need to strip header off before checking for valid json
                json.loads(output.lstrip(HISTORY_TITLE))
            else:  # i.e. fmt_arg == 'jsonl':
                assert output.startswith(HISTORY_TITLE)
                jsonl_output = output.lstrip(HISTORY_TITLE)
                # Newline-delimited json so test each line is valid json
                for line in jsonl_output.splitlines():
                    json.loads(line)


def test_output_argument():
    """Test arguments for the output option."""
    for output_opt in VALID_CMD_OPTS[4]:
        with tempfile.NamedTemporaryFile(suffix=".csv") as f:
            output = subprocess.check_output([CMD_ROOT, output_opt, f.name])
            # Check output was not sent to STDOUT since should go to file
            assert HISTORY_HEADER not in output.decode("utf-8")
            with open(f.name, "rb") as f:  # now check the file
                assert HISTORY_HEADER in f.read().decode("utf-8")


def test_argument_combinations():
    """Test that combinations of optional arguments work properly."""
    # Choose some representative combinations. No need to test every one.
    indices = (0, 1)
    # To test combos of short or long option variants
    for index_a, index_b in itertools.product(indices, indices):
        chrome_bookmarks_output = subprocess.check_output(
            [
                CMD_ROOT,
                VALID_CMD_OPTS[1][index_a],  # type
                VALID_TYPE_ARGS[1],  # ... is bookmarks,
                VALID_CMD_OPTS[2][index_a],  # browser
                VALID_BROWSER_ARGS[1],  # ... is Chrome
            ]
        ).decode("utf-8")
        assert chrome_bookmarks_output.startswith(BOOKMARKS_TITLE)
        assert not chrome_bookmarks_output.startswith(HISTORY_TITLE)
        read_csv = csv.Sniffer()
        read_csv.sniff(chrome_bookmarks_output, delimiters=",")
        assert read_csv.has_header(chrome_bookmarks_output)

        with tempfile.NamedTemporaryFile(suffix=".csv") as f:
            # This command should write to the given output file:
            subprocess.check_output(
                [
                    CMD_ROOT,
                    VALID_CMD_OPTS[3][index_b],  # format
                    VALID_FORMAT_ARGS[2],  # ... is json,
                    VALID_CMD_OPTS[4][index_b],  # output
                    f.name,  # ... is a named file
                ]
            ).decode("utf-8")
            with open(f.name, "rb") as f:
                json.loads(f.read().decode("utf-8"))


def test_help_option():
    """Test the command-line help provided to the user on request."""
    for help_opt in VALID_CMD_OPTS[0]:
        output = subprocess.check_output([CMD_ROOT, help_opt]).decode("utf-8")
        assert HELP_SIGNATURE in output


def test_invalid_options():
    """Test that invalid options error correctly."""
    for bad_opt in INVALID_CMD_OPTS:
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_output([CMD_ROOT, bad_opt]).decode("utf-8")
