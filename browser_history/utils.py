"""
Module defines Platform class enumerates the popular Operating Systems.

"""
import enum
import platform
from browser_history import browsers
from browser_history import generic
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

def get_history():
    """This method is used to obtain browser histories of all available and supported
    browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with the
    data member entries set to list(tuple(:py:class:`datetime.datetime`, str))
    
    :rtype: :py:class:`browser_history.generic.Outputs`
    """
    system = get_platform()
    output_object = generic.Outputs()

    if system == Platform.LINUX:
        chrome = browsers.Chrome()
        chrome_object = chrome.fetch()
        output_object.entries.extend(chrome_object.entries)
        firefox = browsers.Firefox()
        firefox_object = firefox.fetch()
        output_object.entries.extend(firefox_object.entries)
        chromium = browsers.Chromium()
        chromium_object = chromium.fetch()
        output_object.entries.extend(chromium_object.entries)


    elif system == Platform.WINDOWS:
        chrome = browsers.Chrome()
        chrome_object = chrome.fetch()
        output_object.entries.extend(chrome_object.entries)
        firefox = browsers.Firefox()
        firefox_object = firefox.fetch()
        output_object.entries.extend(firefox_object.entries)

    elif system == Platform.MAC:
        safari = browsers.Safari()
        safari_object = safari.fetch()
        output_object.entries.extend(safari_object.entries)
    
    output_object.entries.sort()

    return output_object

