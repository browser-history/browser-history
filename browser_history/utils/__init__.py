"""Assorted helper functions."""
import logging
import subprocess
from typing import List, Optional, Type

from .. import generic

from .platform import get_platform, Platform, get_platform_name

logger = logging.getLogger("browser-history")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def get_browsers() -> List["Type[generic.Browser]"]:
    """Retrieve a list of all browsers implemented by browser_history.

    Returns:
        A :py:class:`list` containing implemented browser classes
        all inheriting from the super class
        :py:class:`browser_history.generic.Browser`.
    """
    return generic.Browser._implemented_browsers


def _default_browser_linux() -> Optional[str]:
    try:
        cmd = "xdg-settings get default-web-browser".split()
        raw_result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        # most have a suffix ".desktop" so just remove it
        default = raw_result.decode().strip().lower().replace(".desktop", "")
    except (FileNotFoundError, subprocess.CalledProcessError, PermissionError):
        logger.warning("Could not determine default browser")
        default = None

    return default


def _default_browser_win() -> Optional[str]:
    if get_platform() == Platform.WINDOWS:
        try:
            import winreg
        except ModuleNotFoundError:
            # TODO: why?
            winreg = None
    reg_path = (
        "Software\\Microsoft\\Windows\\Shell\\Associations\\"
        "UrlAssociations\\https\\UserChoice"
    )
    # TODO: ignore these errors on non-windows platforms?
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
        default = winreg.QueryValueEx(key, "ProgId")
        if default is None:
            logger.warning("Could not determine default browser")
            return None
        return default[0].lower()


def default_browser() -> Optional["Type[generic.Browser]"]:
    """Get the default browser of the current platform.

    Returns:
        A :py:class:`browser_history.generic.Browser` subclass representing the
        default browser in the current platform. If platform is not supported or
        default browser is unknown or unsupported ``None`` is returned.
    """
    plat = get_platform()

    # ---- get default from specific platform ----

    # Always try to return a lower-cased value for ease of comparison
    if plat == Platform.LINUX:
        default = _default_browser_linux()
    elif plat == Platform.WINDOWS:
        default = _default_browser_win()
    else:
        logger.warning("Default browser feature not supported on this OS")
        return None

    if default is None:
        # the current platform has completely failed to provide a default
        logger.warning("No default browser found")
        return None

    # ---- convert obtained default to something we understand ----
    all_browsers = get_browsers()

    # first quick pass for direct matches
    for browser in all_browsers:
        # TODO: fix type errors here
        if default == browser.name.lower() or default in browser._aliases:
            return browser

    # separate pass for deeper matches
    for browser in all_browsers:
        # look for alias matches even if the default name has "noise"
        # for instance firefox on windows returns something like
        # "firefoxurl-3EEDF34567DDE" but we only need "firefoxurl"
        for alias in browser._aliases:
            if alias in default:
                return browser

    # nothing was found
    # TODO: maybe print the detected default browser here?
    #       and ask to specify the browser explicitly?
    logger.warning("Current default browser is not supported")
    return None


def get_browser(browser_name: str) -> Optional["Type[generic.Browser]"]:
    """Get the browser class from its name.

    Args:
        browser_name: a string representing one of the browsers supported
            or ``default`` (to fetch the default browser).

    Returns:
        A browser class which is a subclass of
        :py:class:`browser_history.generic.Browser`. ``None`` if no supported browsers
        match the browser name given or the given browser is not supported on the
        current platform
    """
    # gets browser class by name (string).
    if browser_name == "default":
        return default_browser()
    else:
        browser_class = None
        for browser in get_browsers():
            if browser.__name__.lower() == browser_name.lower():
                if browser.is_supported():
                    browser_class = browser
                    break
                else:
                    logger.error(
                        "%s browser is not supported on %s",
                        browser_name,
                        get_platform_name(),
                    )
                    return

        if browser_class is None:
            logger.error(
                "%s browser is unavailable. Check --help for available browsers",
                browser_name,
            )

        return browser_class
