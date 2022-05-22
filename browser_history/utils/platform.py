"""Helpers for system platform detection and representation."""
import enum
import platform
from typing import Optional


class Platform(enum.Enum):
    """An enum used to indicate the system's platform.

    A value of 0 is reserved for unknown platforms.

    See :py:func:`get_platform` to infer the platform from the system.

    Tip:
        To be used without instantiating like so::

            linux = Platform.LINUX
            mac = Platform.MAC
            windows = Platform.WINDOWS
    """

    OTHER = 0
    LINUX = 1
    MAC = 2
    WINDOWS = 3


def get_platform() -> Platform:
    """Infer the system's platform."""
    system = platform.system()
    if system == "Linux":
        return Platform.LINUX
    if system == "Darwin":
        return Platform.MAC
    if system == "Windows":
        return Platform.WINDOWS
    # TODO: check if this is the right error?
    raise NotImplementedError(f"Platform {system} is not supported yet")


def get_platform_name(plat: Optional[Platform] = None) -> str:
    """Human readable name of the current platform."""
    if plat is None:
        plat = get_platform()

    if plat == Platform.LINUX:
        return "Linux"
    if plat == Platform.WINDOWS:
        return "Windows"
    if plat == Platform.MAC:
        return "MacOS"
    return "Unknown"
