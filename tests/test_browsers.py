import datetime
from pathlib import Path

from .context import browser_history
from .utils import (  # noqa: F401; pylint: disable=unused-import
    become_linux,
    become_mac,
    become_windows,
    change_homedir,
)

# pylint: disable=redefined-outer-name,unused-argument


def test_firefox_linux(become_linux, change_homedir):  # noqa: F811
    """Test history is correct on Firefox for Linux"""
    f = browser_history.browsers.Firefox()
    output = f.fetch_history()
    his = output.histories
    assert len(his) == 5
    assert his[0] == (
        datetime.datetime(
            2020,
            8,
            3,
            0,
            29,
            4,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
        ),
        "https://www.mozilla.org/en-US/privacy/firefox/",
    )
    profs = f.profiles(f.history_file)
    his_path = f.history_path_profile(profs[0])
    assert his_path == Path.home() / ".mozilla/firefox/profile/places.sqlite"
    his = f.history_profiles(profs).histories
    assert len(his) == 5
    assert his[0] == (
        datetime.datetime(
            2020,
            8,
            3,
            0,
            29,
            4,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
        ),
        "https://www.mozilla.org/en-US/privacy/firefox/",
    )

def test_chrome_linux(become_linux, change_homedir):
    """Test history is correct on Chrome for Linux"""
    f = browser_history.browsers.Chrome()
    output = f.fetch_history()
    his = output.histories
    assert len(his) == 2
    assert his[0] == (
        datetime.datetime(
            2020,
            10,
            15,
            15,
            34,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
        ),
        "www.github.com",
    )
    profs = f.profiles(f.history_file)
    his_path = f.history_path_profile(profs[0])
    assert his_path == Path.home() / ".config/google-chrome/History"
    his = f.history_profiles(profs).histories
    assert len(his) == 2
    assert his[0] == (
        datetime.datetime(
            2020,
            10,
            15,
            15,
            34,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
        ),
        "www.github.com",
    )


def test_chromium_linux(become_linux, change_homedir):
    """Test history is correct on Chromium for Linux"""
    f = browser_history.browsers.Chromium()
    output = f.fetch_history()
    his = output.histories
    assert len(his) == 2
    assert his[0] == (
        datetime.datetime(
            2020,
            10,
            15,
            15,
            34,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
        ),
        "www.github.com",
    )
    profs = f.profiles(f.history_file)
    his_path = f.history_path_profile(profs[0])
    assert his_path in [
        Path.home() / ".config/chromium/Default/History",
        Path.home() / ".config/chromium/Profile/History",
    ]
    his = f.history_profiles(profs).histories
    assert len(his) == 2
    assert his[0] == (
        datetime.datetime(
            2020,
            10,
            15,
            15,
            34,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
        ),
        "www.github.com",
    )


def test_firefox_windows(become_windows, change_homedir):  # noqa: F811
    """Test history is correct on Firefox for Windows"""
    f = browser_history.browsers.Firefox()
    output = f.fetch_history()
    his = output.histories
    assert len(his) == 8
    profs = f.profiles(f.history_file)
    assert len(profs) == 2
    # the history list is long so just check the first and last item
    assert his[0] == (
        datetime.datetime(
            2020,
            10,
            1,
            11,
            43,
            35,
            tzinfo=datetime.timezone(
                datetime.timedelta(seconds=10800), "E. Africa Standard Time"
            ),
        ),
        "https://www.youtube.com/",
    )
    assert his[-1] == (
        datetime.datetime(
            2020,
            10,
            4,
            14,
            2,
            14,
            tzinfo=datetime.timezone(
                datetime.timedelta(seconds=10800), "E. Africa Standard Time"
            ),
        ),
        "https://www.reddit.com/",
    )
    # get history for second profile
    his = f.history_profiles(["Profile 2"]).histories
    assert his == [
        (
            datetime.datetime(
                2020,
                10,
                4,
                14,
                2,
                14,
                tzinfo=datetime.timezone(
                    datetime.timedelta(seconds=10800),
                    "E. Africa Standard Time",
                ),
            ),
            "https://www.reddit.com/",
        )
    ]


def test_edge_windows(become_windows, change_homedir):  # noqa: F811
    """Test history is correct for Edge on Windows"""
    e = browser_history.browsers.Edge()
    output = e.fetch_history()
    his = output.histories
    # test history from all profiles
    assert len(his) == 1
    assert his == [
        (
            datetime.datetime(
                2020,
                9,
                23,
                10,
                45,
                3,
                tzinfo=datetime.timezone(
                    datetime.timedelta(seconds=19800), "India Standard Time"
                ),
            ),
            "https://pesos.github.io/",
        ),
    ]

    # test history from specific profile
    profs = e.profiles(e.history_file)
    assert len(profs) == 2
    his_path = e.history_path_profile("Profile 2")
    assert (
        his_path
        == Path.home() / "AppData/Local/Microsoft/Edge/User Data/Profile 2/History"
    )
    his = e.history_profiles(["Profile 2"]).histories
    assert len(his) == 1
    assert his == [
        (
            datetime.datetime(
                2020,
                9,
                23,
                10,
                45,
                3,
                tzinfo=datetime.timezone(
                    datetime.timedelta(seconds=19800), "India Standard Time"
                ),
            ),
            "https://pesos.github.io/",
        )
    ]


def test_safari_mac(become_mac, change_homedir):  # noqa: F811
    """Test history is correct for Safari on macOS"""

    e = browser_history.browsers.Safari()
    output = e.fetch_history()
    his = output.histories
    assert len(his) == 5
    assert his[0] == (
        datetime.datetime(
            2020,
            9,
            29,
            23,
            34,
            28,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
        ),
        "https://www.apple.com/in/",
    )
    assert his[1][1] == "https://www.google.co.in/?client=safari&channel=mac_bm"
    assert his[4] == (
        datetime.datetime(
            2020,
            9,
            29,
            23,
            35,
            8,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
        ),
        "https://pesos.github.io/",
    )


def test_opera_windows(become_windows, change_homedir):
    o = browser_history.browsers.Opera()
    outputs = o.fetch_history()
    his = outputs.histories
    assert len(his) == 2
    assert his == [
        (
            datetime.datetime(
                2020,
                10,
                13,
                12,
                4,
                51,
                tzinfo=datetime.timezone(
                    datetime.timedelta(seconds=10800), "E. Africa Standard Time"
                ),
            ),
            "https://www.youtube.com/",
        ),
        (
            datetime.datetime(
                2020,
                10,
                13,
                12,
                4,
                59,
                tzinfo=datetime.timezone(
                    datetime.timedelta(seconds=10800), "E. Africa Standard Time"
                ),
            ),
            "https://github.com/",
        ),
    ]
    assert len(o.profiles(o.history_file)) == 1
