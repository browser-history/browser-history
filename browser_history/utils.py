import enum
import platform
from pathlib import Path

class Platform(enum.Enum):
    OTHER = 0
    LINUX = 1
    MAC = 2
    WINDOWS = 3

class Browser(enum.Enum):
    CHROME = 1
    FIREFOX = 2
    SAFARI = 3

def get_platform():
    system = platform.system()
    if system == "Linux":
        return Platform.LINUX
    elif system == "Darwin":
        return Platform.MAC
    elif system == "Windows":
        return Platform.WINDOWS
    else:
        raise NotImplementedError(f"Platform {system} is not supported yet")

