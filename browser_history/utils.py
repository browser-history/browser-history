"""
Module defines Platform class enumerates the popular Operating Systems.

"""

import enum
import inspect
import logging
import platform
import subprocess
from typing import Optional

from . import generic

logger = logging.getLogger("browser-history")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Platform(enum.Enum):
    """An enum used to indicate the system's platform

    A value of 0 is reserved for unknown platforms.

    **Usage**:
    To be used without instantiating like so::

        linux = Platform.LINUX
        mac = Platform.MAC
        windows = Platform.WINDOWS

    See :py:func:`get_platform` to infer the platform from the system.
    """

    OTHER = 0
    LINUX = 1
    MAC = 2
    WINDOWS = 3


def get_platform():
    """Returns the current platform

    :rtype: :py:class:`Platform`
    """
    system = platform.system()
    if system == "Linux":
        return Platform.LINUX
    if system == "Darwin":
        return Platform.MAC
    if system == "Windows":
        return Platform.WINDOWS
    raise NotImplementedError(f"Platform {system} is not supported yet")


def get_platform_name(plat: Optional[Platform] = None) -> str:
    """Returns human readable name of the current platform"""
    if plat is None:
        plat = get_platform()

    if plat == Platform.LINUX:
        return "Linux"
    if plat == Platform.WINDOWS:
        return "Windows"
    if plat == Platform.MAC:
        return "MacOS"
    return "Unknown"


def get_browsers():
    """This method provides a list of all browsers implemented by
    browser_history.

    :return: A :py:class:`list` containing implemented browser classes
        all inheriting from the super class
        :py:class:`browser_history.generic.Browser`

    :rtype: :py:class:`list`
    """

    # recursively get all concrete subclasses
    def get_subclasses(browser):
        # include browser itself in return list if it is concrete
        sub_classes = []
        if not inspect.isabstract(browser):
            sub_classes.append(browser)

        for sub_class in browser.__subclasses__():
            sub_classes.extend(get_subclasses(sub_class))
        return sub_classes

    return get_subclasses(generic.Browser)


def _default_browser_linux():
    try:
        cmd = "xdg-settings get default-web-browser".split()
        raw_result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        # most have a suffix ".desktop" so just remove it
        default = raw_result.decode().strip().lower().replace(".desktop", "")
    except (FileNotFoundError, subprocess.CalledProcessError, PermissionError):
        logger.warning("Could not determine default browser")
        default = None

    return default


def _default_browser_win():
    if get_platform() == Platform.WINDOWS:
        try:
            import winreg
        except ModuleNotFoundError:
            winreg = None
    reg_path = (
        "Software\\Microsoft\\Windows\\Shell\\Associations\\"
        "UrlAssociations\\https\\UserChoice"
    )
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
        default = winreg.QueryValueEx(key, "ProgId")
        if default is None:
            logger.warning("Could not determine default browser")
            return None
        return default[0].lower()


def default_browser():
    """This method gets the default browser of the current platform

    :return: A :py:class:`browser_history.generic.Browser` object representing the
        default browser in the current platform. If platform is not supported or
        default browser is unknown or unsupported ``None`` is returned

    :rtype: union[:py:class:`browser_history.generic.Browser`, None]
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
        if default == browser.name.lower() or default in browser.aliases:
            return browser

    # separate pass for deeper matches
    for browser in all_browsers:
        # look for alias matches even if the default name has "noise"
        # for instance firefox on windows returns something like
        # "firefoxurl-3EEDF34567DDE" but we only need "firefoxurl"
        for alias in browser.aliases:
            if alias in default:
                return browser

    # nothing was found
    logger.warning("Current default browser is not supported")
    return None


def get_browser(browser_name):
    """
    This method returns the browser class from a browser name.

    :param browser_name: a string representing one of the browsers supported
        or ``default`` (to fetch the default browser).

    :return: A browser class which is a subclass of
        :py:class:`browser_history.generic.Browser` otherwise ``None`` if no
        supported browsers match the browser name given or the given browser
        is not supported on the current platform

    :rtype: union[:py:class:`browser_history.generic.Browser`, None]
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
