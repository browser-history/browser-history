from browser_history.utils import get_platform, get_platform_name, Platform
from .utils import become_linux, become_mac, become_windows  # noqa: F401


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
