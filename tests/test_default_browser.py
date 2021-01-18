# noqa: F401, F811
# pylint: disable=redefined-outer-name,unused-argument,unused-import

import webbrowser

import pytest

from browser_history.utils import default_browser
from browser_history import browsers

from .utils import become_mac, become_linux  # noqa: F401


class MockBrowser:
    def __init__(self, name=None):
        self.name = name


@pytest.fixture
def change_webbrowser_default(monkeypatch, request):
    """Changes webbrowser.get() to return a specific named
    browser. use @pytest.mark.browser_name(name) to set
    browser name
    """

    marker = request.node.get_closest_marker("browser_name")

    if marker is None:
        browser_name = None
    else:
        browser_name = marker.args[0]

    def mock_get():
        return MockBrowser(name=browser_name)

    monkeypatch.setattr(webbrowser, "get", mock_get)


@pytest.mark.browser_name("firefox")
def test_default_firefox(become_linux, change_webbrowser_default):  # noqa: F811
    """Test that firefox set as default is recognised
    correctly"""
    assert default_browser() == browsers.Firefox


@pytest.mark.browser_name("chromehtml")
def test_default_chrome(become_linux, change_webbrowser_default):  # noqa: F811
    """Test that Chrome set as default is recognised
    correctly"""
    assert default_browser() == browsers.Chrome


@pytest.mark.browser_name("safari")
def test_default_safari(become_mac, change_webbrowser_default):  # noqa: F811
    """Test that Safari set as default in MacOS is NOT
    recognised correctly since default browser in MacOS is not
    supported."""
    assert default_browser() is None
