from pathlib import Path
import platform
import pytest


@pytest.fixture()
def change_homedir(monkeypatch):
    """Change home directory for all tests"""
    monkeypatch.setattr(
        Path, "home", lambda: Path(f"./tests/test_homedirs/{platform.system()}")
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
