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
