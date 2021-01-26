# noqa: F401, F811
# pylint: disable=redefined-outer-name,unused-argument,unused-import

import webbrowser

import pytest

from browser_history import browsers, utils

from .utils import become_mac, become_linux, become_windows  # noqa: F401


platform = utils.get_platform()


class MockBrowser:
    """Mock version of return value of webbrowser.get()"""

    def __init__(self, name=None):
        self.name = name


@pytest.fixture
def change_linux_default(monkeypatch, request):
    """Changes utils._default_browser_linux to return a specific named
    browser. use @pytest.mark.browser_name(name) to set
    browser name
    """

    marker = request.node.get_closest_marker("browser_name")

    if marker is None:
        browser_name = None
    else:
        browser_name = marker.args[0]

    def mock_get():
        return browser_name

    monkeypatch.setattr(utils, "_default_browser_linux", mock_get)


@pytest.fixture
def change_win_default(monkeypatch, request):
    """Changes utils._default_browser_win to return a specific named
    browser. use @pytest.mark.browser_name(name) to set
    browser name
    """
    if platform != utils.Platform.WINDOWS:
        pytest.skip("Skipping windows registry based test")

    marker = request.node.get_closest_marker("browser_name")

    if marker is None:
        browser_name = None
    else:
        browser_name = marker.args[0]

    def mock_get():
        return browser_name

    monkeypatch.setattr(utils, "_default_browser_win", mock_get)


@pytest.mark.browser_name("firefox")
def test_default_firefox(become_linux, change_linux_default):  # noqa: F811
    """Test that firefox set as default is recognised
    correctly"""
    assert utils.default_browser() == browsers.Firefox


@pytest.mark.browser_name("chromehtml")
def test_default_chrome(become_linux, change_linux_default):  # noqa: F811
    """Test that Chrome set as default is recognised
    correctly"""
    assert utils.default_browser() == browsers.Chrome


def test_default_none(become_linux, change_linux_default):  # noqa: F811
    """Test that no default set returns None"""
    assert utils.default_browser() is None


@pytest.mark.browser_name("safari")
def test_default_safari(become_mac, change_linux_default):  # noqa: F811
    """Test that Safari set as default in MacOS is NOT
    recognised correctly since default browser in MacOS is not
    supported."""
    assert utils.default_browser() is None


@pytest.mark.browser_name("chromehtml")
def test_default_windows_chrome(
    become_windows, change_win_default  # noqa: F811
):
    """Test that chrome is identified correctly on Windows"""
    assert utils.default_browser() == browsers.Chrome


@pytest.mark.browser_name("firefoxurl")
def test_default_windows_firefox(
    become_windows, change_win_default  # noqa: F811
):
    """Test that firefox is identified correctly on Windows"""
    assert utils.default_browser() == browsers.Firefox


def test_default_windows_none(become_windows, change_win_default):  # noqa: F811
    """Test that registry returning None is handled correctly"""
    assert utils.default_browser() is None
