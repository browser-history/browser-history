import sys
from unittest.mock import patch, Mock, MagicMock

import pytest

from browser_history.utils import (
    get_platform,
    get_platform_name,
    Platform,
    _default_browser_linux,
    _default_browser_win,
    default_browser,
    get_browser,
)
from .utils import (  # noqa: F401
    become_linux,
    become_mac,
    become_windows,
    become_unknown,
)


def test_plat_linux(become_linux):  # noqa: F811
    assert get_platform() == Platform.LINUX


def test_plat_mac(become_mac):  # noqa: F811
    assert get_platform() == Platform.MAC


def test_plat_win(become_windows):  # noqa: F811
    assert get_platform() == Platform.WINDOWS


def test_platform_name_linux(become_linux):  # noqa: F811
    assert get_platform_name() == "Linux"


def test_platform_name_mac(become_mac):  # noqa: F811
    assert get_platform_name() == "MacOS"


def test_platform_name_win(become_windows):  # noqa: F811
    assert get_platform_name() == "Windows"


def test_platform_name_unknown(become_unknown):  # noqa: F811
    with pytest.raises(NotImplementedError):
        get_platform_name()


def test__default_browser_linux_process_execution_successful():
    mocked_sp = Mock()
    mocked_sp.check_output.return_value = b"default.desktop"
    with patch("browser_history.utils.subprocess", mocked_sp):
        default = _default_browser_linux()
    assert default == "default"


def test__default_browser_linux_process_execution_fail():
    with patch(
        "browser_history.utils.subprocess.check_output", side_effect=PermissionError
    ):
        default = _default_browser_linux()
    assert default is None


def test__default_browser_win_key_has_value(become_windows):  # noqa: F811
    mocked_winreg = MagicMock()
    mocked_winreg.QueryValueEx.return_value = ["DEFAULT"]
    sys.modules["winreg"] = mocked_winreg
    default = _default_browser_win()
    sys.modules.pop("winreg")
    assert default == "default"


def test__default_browser_win_key_is_empty(become_windows):  # noqa: F811
    mocked_winreg = MagicMock()
    mocked_winreg.QueryValueEx.return_value = None
    sys.modules["winreg"] = mocked_winreg
    default = _default_browser_win()
    sys.modules.pop("winreg")
    assert default is None


def test_default_browser_firefox_noisy_alias(become_windows):  # noqa: F811
    mocked_dbw = Mock()
    mocked_dbw.return_value = "garbage_firefoxurl"
    with patch("browser_history.utils._default_browser_win", mocked_dbw):
        browser = default_browser()
    assert browser.name == "Firefox"


def test_default_browser_unknown_alias(become_windows):  # noqa: F811
    mocked_dbw = Mock()
    mocked_dbw.return_value = "garbage"
    with patch("browser_history.utils._default_browser_win", mocked_dbw):
        browser = default_browser()
    assert browser is None


def test_get_browser_default_name(become_windows):  # noqa: F811
    mocked_dbw = Mock()
    mocked_dbw.return_value = "firefoxurl"
    with patch("browser_history.utils._default_browser_win", mocked_dbw):
        browser = get_browser("default")
    assert browser.name == "Firefox"
