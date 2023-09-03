import datetime
from pathlib import Path

from .context import browser_history
from .utils import (  # noqa: F401; pylint: disable=unused-import
    become_linux,
    become_mac,
    become_windows,
    change_homedir,
    assert_histories_equal,
    assert_bookmarks_equal,
)

import pytest


# pylint: disable=redefined-outer-name,unused-argument


@pytest.mark.parametrize(
    "browser_type, bookmark_dir",
    [
        (browser_history.browsers.Firefox, ".mozilla/firefox/profile/places.sqlite"),
        (
            browser_history.browsers.FirefoxSnap,
            "snap/firefox/common/.mozilla/firefox/profile/places.sqlite",
        ),
    ],
)
def test_firefox_linux(
    become_linux, change_homedir, browser_type, bookmark_dir  # noqa: F811
):
    """Test history is correct on Firefox for Linux"""
    f = browser_type()
    h_output = f.fetch_history()
    b_output = f.fetch_bookmarks()
    his = h_output.histories
    bmk = b_output.bookmarks
    assert len(his) == 5
    assert len(bmk) == 30
    assert_histories_equal(
        his[0],
        (
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
            "Firefox Privacy Notice — Mozilla",
        ),
    )
    assert_bookmarks_equal(
        bmk[0],
        (
            datetime.datetime(
                2005,
                11,
                3,
                3,
                14,
                56,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://forums.fedoraforum.org/",
            "Fedora Forum",
            "User Communities",
        ),
    )
    profs = f.profiles(f.history_file)
    his_path = f.history_path_profile(profs[0])
    bmk_path = f.bookmarks_path_profile(profs[0])
    assert his_path == bmk_path == Path.home() / bookmark_dir
    his = f.history_profiles(profs).histories
    # >>>>>>> 1042e11 ([TESTS] add test for empty history file)
    assert len(his) == 5
    assert_histories_equal(
        his[0],
        (
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
            "Firefox Privacy Notice — Mozilla",
        ),
    )


@pytest.mark.parametrize(
    "browser_type",
    [
        browser_history.browsers.Firefox,
        browser_history.browsers.FirefoxSnap,
    ],
)
def test_empty_history_file(become_linux, change_homedir, browser_type):  # noqa: F811
    f = browser_type()
    out = f.history_profiles(["empty"])

    assert len(out.histories) == 0


def test_chrome_linux(become_linux, change_homedir):  # noqa: F811
    """Test history is correct on Chrome for Linux"""
    f = browser_history.browsers.Chrome()
    h_output = f.fetch_history()
    b_output = f.fetch_bookmarks()
    his = h_output.histories
    bmk = b_output.bookmarks
    assert len(his) == 2
    assert len(bmk) == 5
    assert_histories_equal(
        his[0],
        (
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
            "GitHub: Where the world builds software · GitHub",
        ),
    )
    assert_bookmarks_equal(
        bmk[0],
        (
            datetime.datetime(
                2021,
                2,
                9,
                9,
                37,
                32,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://github.com/pesos/browser-history",
            "Browser-history",
            "bookmark_bar/github",
        ),
    )
    h_profs = f.profiles(f.history_file)
    b_profs = f.profiles(f.bookmarks_file)
    his_path = f.history_path_profile(h_profs[0])
    bmk_path = f.bookmarks_path_profile(b_profs[0])
    assert his_path == Path.home() / ".config/google-chrome/History"
    assert bmk_path == Path.home() / ".config/google-chrome/Bookmarks"
    his = f.history_profiles(h_profs).histories
    assert len(his) == 2
    assert_histories_equal(
        his[0],
        (
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
            "GitHub: Where the world builds software · GitHub",
        ),
    )


def test_chromium_linux(become_linux, change_homedir):  # noqa: F811
    """Test history is correct on Chromium for Linux"""
    f = browser_history.browsers.Chromium()
    h_output = f.fetch_history()
    b_output = f.fetch_bookmarks()
    his = h_output.histories
    bmk = b_output.bookmarks
    assert len(his) == 2
    assert len(bmk) == 10
    assert_histories_equal(
        his[0],
        (
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
            "GitHub: Where the world builds software · GitHub",
        ),
    )
    assert_bookmarks_equal(
        bmk[0],
        (
            datetime.datetime(
                2021,
                2,
                9,
                9,
                37,
                32,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://github.com/pesos/browser-history",
            "Browser-history",
            "bookmark_bar/github",
        ),
    )
    h_profs = f.profiles(f.history_file)
    b_profs = f.profiles(f.bookmarks_file)
    his_path = f.history_path_profile(h_profs[0])
    bmk_path = f.bookmarks_path_profile(b_profs[0])
    assert his_path in [
        Path.home() / ".config/chromium/Default/History",
        Path.home() / ".config/chromium/Profile/History",
    ]
    assert bmk_path in [
        Path.home() / ".config/chromium/Default/Bookmarks",
        Path.home() / ".config/chromium/Profile/Bookmarks",
    ]
    his = f.history_profiles(h_profs).histories
    assert len(his) == 2
    assert_histories_equal(
        his[0],
        (
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
            "GitHub: Where the world builds software · GitHub",
        ),
    )


def test_firefox_windows(become_windows, change_homedir):  # noqa: F811
    """Test history is correct on Firefox for Windows"""
    f = browser_history.browsers.Firefox()
    h_output = f.fetch_history()
    b_output = f.fetch_bookmarks()
    his = h_output.histories
    bmk = b_output.bookmarks
    assert len(his) == 8
    assert len(bmk) == 14
    profs = f.profiles(f.history_file)
    assert len(profs) == 2
    # the history list is long so just check the first and last item
    assert_histories_equal(
        his[0],
        (
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
            "YouTube",
        ),
    )
    assert_bookmarks_equal(
        bmk[0],
        (
            datetime.datetime(
                2018,
                12,
                8,
                0,
                33,
                27,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "http://dl.dlb3d.xyz/S/",
            "Index of /S/",
            "unfiled",
        ),
    )
    assert_histories_equal(
        his[-1],
        (
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
            "reddit: the front page of the internet",
        ),
    )
    # get history for second profile
    his = f.history_profiles(["Profile 2"]).histories
    assert_histories_equal(
        his[0],
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
            "reddit: the front page of the internet",
        ),
    )


def test_edge_windows(become_windows, change_homedir):  # noqa: F811
    """Test history is correct for Edge on Windows"""
    e = browser_history.browsers.Edge()
    output = e.fetch_history()
    his = output.histories
    # test history from all profiles
    assert len(his) == 1
    assert_histories_equal(
        his[0],
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
            "Welcome to PES Open Source - PES Open Source",
        ),
    )

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
    assert_histories_equal(
        his[0],
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
            "Welcome to PES Open Source - PES Open Source",
        ),
    )


def test_safari_mac(become_mac, change_homedir):  # noqa: F811
    """Test history is correct for Safari on macOS"""

    e = browser_history.browsers.Safari()
    output = e.fetch_history()
    his = output.histories
    assert len(his) == 5
    assert_histories_equal(
        his[0],
        (
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
            "",
        ),
    )
    assert his[1][1] == "https://www.google.co.in/?client=safari&channel=mac_bm"
    assert_histories_equal(
        his[4],
        (
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
            None,
        ),
    )


def test_opera_windows(become_windows, change_homedir):  # noqa: F811
    o = browser_history.browsers.Opera()
    h_output = o.fetch_history()
    b_output = o.fetch_bookmarks()
    his = h_output.histories
    bmk = b_output.bookmarks
    assert len(his) == 2
    assert len(bmk) == 4
    assert_histories_equal(
        his[0],
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
            "YouTube",
        ),
    )
    assert_bookmarks_equal(
        bmk[0],
        (
            datetime.datetime(
                2021,
                2,
                17,
                13,
                52,
                41,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://www.google.com/",
            "Google",
            "bookmark_bar",
        ),
    )
    assert len(his) == 2
    assert_histories_equal(
        his[1],
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
            "GitHub: Where the world builds software · GitHub",
        ),
    )
    assert len(o.profiles(o.history_file)) == 1


def test_brave_windows(become_windows, change_homedir):  # noqa: F811
    """Test history is correct on Brave for Windows"""
    f = browser_history.browsers.Brave()
    h_output = f.fetch_history()
    b_output = f.fetch_bookmarks()
    his = h_output.histories
    bmk = b_output.bookmarks
    assert len(his) == 4
    assert len(bmk) == 4
    profs = f.profiles(f.history_file)
    assert len(profs) == 2
    # check first and last item to ensure both profiles are searched
    assert_histories_equal(
        his[0],
        (
            datetime.datetime(
                2020,
                12,
                7,
                21,
                58,
                11,
                tzinfo=datetime.timezone(
                    datetime.timedelta(seconds=10800), "E. Africa Standard Time"
                ),
            ),
            "https://github.com/",
            "GitHub: Where the world builds software · GitHub",
        ),
    )
    assert_bookmarks_equal(
        bmk[0],
        (
            datetime.datetime(
                2021,
                2,
                17,
                13,
                52,
                41,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://www.google.com/",
            "Google",
            "bookmark_bar",
        ),
    )
    assert_histories_equal(
        his[-1],
        (
            datetime.datetime(
                2020,
                12,
                7,
                22,
                1,
                29,
                tzinfo=datetime.timezone(
                    datetime.timedelta(seconds=10800), "E. Africa Standard Time"
                ),
            ),
            "https://stackoverflow.com/",
            "Stack Overflow - Where Developers Learn, Share, & Build Careers",
        ),
    )
    # get history for second profile
    his = f.history_profiles(["Profile 2"]).histories
    assert_histories_equal(
        his[0],
        (
            datetime.datetime(
                2020,
                12,
                7,
                22,
                0,
                40,
                tzinfo=datetime.timezone(
                    datetime.timedelta(seconds=10800), "E. Africa Standard Time"
                ),
            ),
            "https://www.reddit.com/",
            "reddit: the front page of the internet",
        ),
    )


def test_vivaldi_mac(become_mac, change_homedir):  # noqa: F811
    """Test history is correct on Vivaldi for MacOS"""
    f = browser_history.browsers.Vivaldi()
    output = f.fetch_history()
    his = output.histories
    assert len(his) == 2
    profs = f.profiles(f.history_file)
    assert len(profs) == 1
    # check first and last item to ensure both profiles are searched
    assert_histories_equal(
        his[0],
        (
            datetime.datetime(
                2021,
                1,
                25,
                14,
                25,
                3,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://vivaldi.com/whats-new-in-vivaldi-3-5/",
            "What’s New in Vivaldi 3.5 | Vivaldi Browser",
        ),
    )

    his = f.history_profiles(["Profile 1"]).histories
    assert_histories_equal(
        his[1],
        (
            datetime.datetime(
                2021,
                1,
                25,
                14,
                25,
                27,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://pesos.github.io/",
            "Welcome to PES Open Source - PES Open Source",
        ),
    )


def test_librewolf_linux(become_linux, change_homedir):  # noqa: F811
    """Test history is correct on LibreWolf for Linux"""
    f = browser_history.browsers.LibreWolf()
    h_output = f.fetch_history()
    b_output = f.fetch_bookmarks()
    his = h_output.histories
    bmk = b_output.bookmarks
    assert len(his) == 12
    assert len(bmk) == 1

    assert_histories_equal(
        his[0],
        (
            datetime.datetime(
                2021,
                9,
                20,
                17,
                48,
                21,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://duckduckgo.com/?t=ffab&q=fhgi",
            "fhgi at DuckDuckGo",
        ),
    )

    assert_bookmarks_equal(
        bmk[0],
        (
            datetime.datetime(
                2021,
                9,
                20,
                18,
                17,
                30,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
            ),
            "https://github.com/",
            "GitHub: Where the world builds software · GitHub",
            "menu",
        ),
    )
