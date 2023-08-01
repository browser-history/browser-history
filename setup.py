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

if __name__ == "__main__":
    setuptools.setup()
