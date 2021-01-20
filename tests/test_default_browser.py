# noqa: F401, F811
# pylint: disable=redefined-outer-name,unused-argument,unused-import

import webbrowser

import pytest

from browser_history.utils import default_browser, get_platform, Platform
from browser_history import browsers

from .utils import become_mac, become_linux, become_windows  # noqa: F401


platform = get_platform()
if platform == Platform.WINDOWS:
    import winreg


class MockBrowser:
    """Mock version of return value of webbrowser.get()"""

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


@pytest.fixture
def change_reg_browser_default(monkeypatch, request):
    """Changes webbrowser.get() to return a specific named
    browser. use @pytest.mark.browser_name(name) to set
    browser name
    """
    if platform != Platform.WINDOWS:
        pytest.skip("Skipping windows registry based test")

    marker = request.node.get_closest_marker("browser_name")

    if marker is None:
        browser_name = None
    else:
        browser_name = marker.args[0]

    def mock_QueryValueEx(key1, key2):
        return [browser_name] if browser_name is not None else None

    monkeypatch.setattr(winreg, "QueryValueEx", mock_QueryValueEx)


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


def test_default_none(become_linux, change_webbrowser_default):  # noqa: F811
    """Test that no default set returns None"""
    assert default_browser() is None


@pytest.mark.browser_name("safari")
def test_default_safari(become_mac, change_webbrowser_default):  # noqa: F811
    """Test that Safari set as default in MacOS is NOT
    recognised correctly since default browser in MacOS is not
    supported."""
    assert default_browser() is None


@pytest.mark.browser_name("chromehtml")
def test_default_windows_chrome(
    become_windows, change_reg_browser_default  # noqa: F811
):
    """Test that chrome is identified correctly on Windows"""
    assert default_browser() == browsers.Chrome


@pytest.mark.browser_name("firefoxurl")
def test_default_windows_firefox(
    become_windows, change_reg_browser_default  # noqa: F811
):
    """Test that firefox is identified correctly on Windows"""
    assert default_browser() == browsers.Firefox


def test_default_windows_none(become_windows, change_reg_browser_default):  # noqa: F811
    """Test that registry returning None is handled correctly"""
    assert default_browser() is None
