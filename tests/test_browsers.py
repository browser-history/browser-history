import datetime
from pathlib import Path

from .context import browser_history
from .utils import (  # noqa: F401; pylint: disable=unused-import
    become_linux,
    become_mac,
    become_windows,
    change_homedir,
)

# Note: from Python >= 3.9 it is possible to use a built-in module, zoneinfo,
# (https://docs.python.org/3/library/zoneinfo.html) to achieve timezone
# awareness. For earlier versions, an external module must be used. Choose:
from dateutil import tz


# Instead setting this to the standard library timezone option:
#     datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
# will cause failures for timezones e.g. 'Europe/London'
# or 'Australia/Melbourne' due to DST effects.
LOCAL_TIMEZONE = tz.gettz()


def _detatch_timezone_stamp(hist):
    """Remove the timezone associated with the datetime in a history entry.

    This is so the datetimes can be tested for correctness despite timezone
    complications. Without removing the timezone stamp, we are comparing
    objects like the following, where the timezones are equivalent but named
    differently due to the means of extracting them:

        datetime.datetime(<datetime tuple>, tzinfo=datetime.timezone(
            datetime.timedelta(seconds=<delta>), 'AEDT'))

        datetime.datetime(<datetime tuple>, tzinfo=tzfile('/etc/localtime')

    but the datetime tuple should be, and is tested to be, the same in
    both cases.
    """
    return (hist[0].replace(tzinfo=None), hist[1])


# pylint: disable=redefined-outer-name,unused-argument


def test_firefox_linux(become_linux, change_homedir):  # noqa: F811
    """Test history is correct on Firefox for Linux"""
    f = browser_history.browsers.Firefox()
    output = f.fetch_history()
    his = output.histories
    assert len(his) == 5
    assert _detatch_timezone_stamp(his[0]) == (
        datetime.datetime(
            2020,
            8,
            3,
            0,
            29,
            4,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://www.mozilla.org/en-US/privacy/firefox/",
    )
    profs = f.profiles(f.history_file)
    his_path = f.history_path_profile(profs[0])
    assert his_path == Path.home() / ".mozilla/firefox/profile/places.sqlite"
    his = f.history_profiles(profs).histories
    assert len(his) == 5
    assert _detatch_timezone_stamp(his[0]) == (
        datetime.datetime(
            2020,
            8,
            3,
            0,
            29,
            4,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://www.mozilla.org/en-US/privacy/firefox/",
    )


def test_chrome_linux(become_linux, change_homedir):  # noqa: F811
    """Test history is correct on Chrome for Linux"""
    f = browser_history.browsers.Chrome()
    output = f.fetch_history()
    his = output.histories
    assert len(his) == 2
    assert _detatch_timezone_stamp(his[0]) == (
        datetime.datetime(
            2020,
            10,
            15,
            15,
            34,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "www.github.com",
    )
    profs = f.profiles(f.history_file)
    his_path = f.history_path_profile(profs[0])
    assert his_path == Path.home() / ".config/google-chrome/History"
    his = f.history_profiles(profs).histories
    assert len(his) == 2
    assert _detatch_timezone_stamp(his[0]) == (
        datetime.datetime(
            2020,
            10,
            15,
            15,
            34,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "www.github.com",
    )


def test_chromium_linux(become_linux, change_homedir):  # noqa: F811
    """Test history is correct on Chromium for Linux"""
    f = browser_history.browsers.Chromium()
    output = f.fetch_history()
    his = output.histories
    assert len(his) == 2
    assert _detatch_timezone_stamp(his[0]) == (
        datetime.datetime(
            2020,
            10,
            15,
            15,
            34,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
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
    assert _detatch_timezone_stamp(his[0]) == (
        datetime.datetime(
            2020,
            10,
            15,
            15,
            34,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
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
    assert _detatch_timezone_stamp(his[0]) == (
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
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://www.youtube.com/",
    )
    assert _detatch_timezone_stamp(his[-1]) == (
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
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://www.reddit.com/",
    )
    # get history for second profile
    his = f.history_profiles(["Profile 2"]).histories
    assert _detatch_timezone_stamp(his[0]) == (
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
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://www.reddit.com/",
    )


def test_edge_windows(become_windows, change_homedir):  # noqa: F811
    """Test history is correct for Edge on Windows"""
    e = browser_history.browsers.Edge()
    output = e.fetch_history()
    his = output.histories
    # test history from all profiles
    assert len(his) == 1
    assert _detatch_timezone_stamp(his[0]) == (
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
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://pesos.github.io/",
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
    assert _detatch_timezone_stamp(his[0]) == (
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
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://pesos.github.io/",
    )


def test_safari_mac(become_mac, change_homedir):  # noqa: F811
    """Test history is correct for Safari on macOS"""

    e = browser_history.browsers.Safari()
    output = e.fetch_history()
    his = output.histories
    assert len(his) == 5
    assert _detatch_timezone_stamp(his[0]) == (
        datetime.datetime(
            2020,
            9,
            29,
            23,
            34,
            28,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://www.apple.com/in/",
    )
    assert his[1][1] == "https://www.google.co.in/?client=safari&channel=mac_bm"
    assert _detatch_timezone_stamp(his[4]) == (
        datetime.datetime(
            2020,
            9,
            29,
            23,
            35,
            8,
            tzinfo=datetime.timezone(datetime.timedelta(seconds=19800), "IST"),
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://pesos.github.io/",
    )


def test_opera_windows(become_windows, change_homedir):  # noqa: F811
    o = browser_history.browsers.Opera()
    outputs = o.fetch_history()
    his = outputs.histories
    assert len(his) == 2
    assert _detatch_timezone_stamp(his[0]) == (
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
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://www.youtube.com/",
    )
    assert len(his) == 2
    assert _detatch_timezone_stamp(his[1]) == (
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
        )
        .astimezone(LOCAL_TIMEZONE)
        .replace(tzinfo=None),
        "https://github.com/",
    )
    assert len(o.profiles(o.history_file)) == 1
