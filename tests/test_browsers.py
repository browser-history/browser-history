import datetime
from pathlib import Path

from .context import browser_history
from .utils import become_linux, become_windows, change_homedir # pylint: disable=unused-import

# pylint: disable=redefined-outer-name,unused-argument

def test_firefox_linux(become_linux, change_homedir):
    """Test history is correct on Firefox for Linux"""
    f = browser_history.browsers.Firefox()
    output = f.fetch()
    his = output.get()
    assert len(his) == 1
    assert his == [(datetime.datetime(2020, 8, 3, 0, 29, 4,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=19800),
                                                               'IST')),
                    'https://www.mozilla.org/en-US/privacy/firefox/')]
    profs = f.profiles()
    his_path = f.history_path_profile(profs[0])
    assert his_path == Path.home() / '.mozilla/firefox/profile/places.sqlite'
    his = f.history_profiles(profs).get()
    assert len(his) == 1
    assert his == [(datetime.datetime(2020, 8, 3, 0, 29, 4,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=19800),
                                                               'IST')),
                    'https://www.mozilla.org/en-US/privacy/firefox/')]

def test_edge_windows(become_windows, change_homedir):
    """Test history is correct for Edge on Windows"""
    e = browser_history.browsers.Edge()
    output = e.fetch()
    his = output.get()
    # test history from all profiles
    assert len(his) == 3
    assert his == [(datetime.datetime(2020, 9, 23, 10, 22, 37,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=19800),
                                                               'India Standard Time')),
                    'http://www.google.com/'),
                   (datetime.datetime(2020, 9, 23, 10, 22, 37,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=19800),
                                                               'India Standard Time')),
                    'https://www.google.com/?gws_rd=ssl'),
                   (datetime.datetime(2020, 9, 23, 10, 45, 3,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=19800),
                                                               'India Standard Time')),
                    'https://pesos.github.io/')]

    # test history from specific profile
    profs = e.profiles()
    assert len(profs) == 2
    his_path = e.history_path_profile("Profile 2")
    assert his_path == Path.home() / \
                       'AppData/Local/Microsoft/Edge/User Data/Profile 2/History'
    his = e.history_profiles(["Profile 2"]).get()
    assert len(his) == 1
    assert his == [(datetime.datetime(2020, 9, 23, 10, 45, 3,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=19800),
                                                               'India Standard Time')),
                    'https://pesos.github.io/')]
