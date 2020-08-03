from datetime import datetime

from .context import browser_history
from .utils import become_linux, change_homedir # pylint: disable=unused-import

# pylint: disable=redefined-outer-name,unused-argument

def test_firefox_linux(become_linux, change_homedir):
    """Test history is correct on Firefox for Linux"""
    f = browser_history.browsers.Firefox()
    his = f.history()
    print(his)
    assert len(his) == 1
    assert his == [(datetime(2020, 8, 3, 0, 29, 4),
                    'https://www.mozilla.org/en-US/privacy/firefox/')]
