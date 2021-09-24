"""
browser-history's setup.

browser-history is a simple, zero-dependencies, developer-friendly
python package to retrieve (almost) any browser's history on (almost)
any platform.

See https://browser-history.readthedocs.io/en/stable/ for more help.
"""

try:
    import setuptools
except ImportError:
    raise RuntimeError(
        "Could not install browser-history in the environment as setuptools "
        "is missing. Please create a new virtual environment before proceeding"
    )

import platform

MIN_PYTHON_VERSION = ("3", "6")

if platform.python_version_tuple() < MIN_PYTHON_VERSION:
    raise SystemExit(
        "Could not install browser-history in the environment. The"
        " browser-history package requires python version 3.6+, you are using "
        f"{platform.python_version()}"
    )

if __name__ == "__main__":
    setuptools.setup()
