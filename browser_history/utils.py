"""
Module defines Platform class enumerates the popular Operating Systems.

"""
import enum
import inspect
import logging
import platform
import webbrowser

from . import generic

logger = logging.getLogger(__name__)
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


if get_platform() == Platform.WINDOWS:
    from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx  # type: ignore


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


def default_browser():
    """This method gets the default browser of the current platform

    :return: A :py:class:`browsers.Browser` object representing the default
        browser in the current platform. If platform is not supported or
        default browser is unknown or unsupported ``None`` is returned

    :rtype: union[:py:class:`browsers.Browser`, None]
    """
    plat = get_platform()

    # ---- get default from specific platform ----

    # Always try to return a lower-cased value for ease of comparison
    if plat == Platform.LINUX:
        default = webbrowser.get().name.lower()
    elif plat == Platform.WINDOWS:
        reg_path = (
            "Software\\Microsoft\\Windows\\Shell\\Associations\\"
            "UrlAssociations\\https\\UserChoice"
        )
        with OpenKey(HKEY_CURRENT_USER, reg_path) as key:
            default = QueryValueEx(key, "ProgId")[0].lower()
    else:
        logger.warning("Default browser feature not supported on this OS")
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
