from dateutil import tz
from os import path
import platform
from pathlib import Path

import pytest


@pytest.fixture()
def change_homedir(monkeypatch):
    """Change home directory for all tests"""

    # Safe approach to locating 'tests/' dir (always the dir of this module)
    test_dir = path.dirname(path.abspath(__file__))
    monkeypatch.setattr(
        Path,
        "home",
        lambda: Path(f"{test_dir}/test_homedirs/{platform.system()}"),
    )

    return platform.system()


@pytest.fixture()
def become_windows(monkeypatch):
    """Changes platform.system to return Windows"""
    monkeypatch.setattr(platform, "system", lambda: "Windows")

    return platform.system()


@pytest.fixture()
def become_mac(monkeypatch):
    """Changes platform.system to return Darwin (codename for Mac OS)"""
    monkeypatch.setattr(platform, "system", lambda: "Darwin")

    return platform.system()


@pytest.fixture()
def become_linux(monkeypatch):
    """Changes platform.system to return Linux"""
    monkeypatch.setattr(platform, "system", lambda: "Linux")

    return platform.system()


@pytest.fixture()
def become_unknown(monkeypatch):
    """Changes platform.system to return unknown"""
    monkeypatch.setattr(platform, "system", lambda: "unknown")

    return platform.system()


def _detach_timezone_stamp(hist):
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
    return (hist[0].replace(tzinfo=None), hist[1:])


def assert_histories_equal(actual_history, expected_history):
    """Assert that two histories are equal, accounting for differing timezones.

    Use of any Python standard library timezone-management option, such as:

        datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

    instead of a dedicated external library, notably here dateutil.tz, would
    result in failures for certain timezones e.g. 'Europe/London' or
    'Australia/Melbourne' due to DST effects.

    Note that from Python >= 3.9 it is possible to use a built-in module,
    zoneinfo (https://docs.python.org/3/library/zoneinfo.html) to achieve
    timezone awareness. For earlier versions, an external module must be used.
    """
    local_timezone = tz.gettz()
    assert _detach_timezone_stamp(actual_history) == _detach_timezone_stamp(
        (expected_history[0].astimezone(local_timezone), *expected_history[1:])
    )


def assert_bookmarks_equal(actual_bookmarks, expected_bookmarks):
    """Assert that two bookmarks are equal, accounting for differing timezones.

    Use of any Python standard library timezone-management option, such as:

        datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

    instead of a dedicated external library, notably here dateutil.tz, would
    result in failures for certain timezones e.g. 'Europe/London' or
    'Australia/Melbourne' due to DST effects.

    Note that from Python >= 3.9 it is possible to use a built-in module,
    zoneinfo (https://docs.python.org/3/library/zoneinfo.html) to achieve
    timezone awareness. For earlier versions, an external module must be used.
    """
    local_timezone = tz.gettz()

    actual = (actual_bookmarks[0], actual_bookmarks[1:-1], Path(actual_bookmarks[-1]))
    expected = (
        expected_bookmarks[0].astimezone(local_timezone),
        expected_bookmarks[1:-1],
        Path(expected_bookmarks[-1]),
    )
    assert _detach_timezone_stamp(actual) == _detach_timezone_stamp(expected)
