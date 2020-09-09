import datetime
from pathlib import Path

from .context import browser_history
from .utils import become_linux, change_homedir # pylint: disable=unused-import

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
    his = f.history_profiles(profs)
    assert len(his) == 1
    assert his == [(datetime.datetime(2020, 8, 3, 0, 29, 4,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=19800),
                                                               'IST')),
                    'https://www.mozilla.org/en-US/privacy/firefox/')]
