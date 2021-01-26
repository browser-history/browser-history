# browser-history

![tests](https://github.com/pesos/browser-history/workflows/tests/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/browser-history/badge/?version=latest)](https://browser-history.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/browser-history.svg)](https://badge.fury.io/py/browser-history)
[![codecov](https://codecov.io/gh/pesos/browser-history/branch/master/graph/badge.svg)](https://codecov.io/gh/pesos/browser-history)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintainability](https://api.codeclimate.com/v1/badges/64c86a28b0d7d387ce72/maintainability)](https://codeclimate.com/github/pesos/browser-history/maintainability)

``browser-history`` is a simple, zero-dependencies, developer-friendly python
package to retrieve (almost) any browser's history on (almost) any platform.


## Features

 - Supports most **popular browsers**. See [this](https://browser-history.readthedocs.io/en/latest/browsers.html) for a full list.
 - Supports all major platforms - **Windows, Mac and Linux**.
 - A **command-line tool**: simply run `browser-history --help` from your terminal.
 - **History**: browsing history with exact timestamp and URL.
 - **Bookmarks**: browser bookmarks with timestamp, URL, title and folder.
 - Lightweight: the entire package is less than 20kB in size and has no dependencies other than python 3.6+.
 - Developer friendly: you can add support for new browsers or add a new feature very easily.
 - Default browser: can automatically determine the default browser on Windows and Linux (`browser-history -b default`).
 - Fully open source: this project is developed and maintained by [PES Open Source](https://github.com/pesos) and will always be open source (with the Apache 2.0 License).

# Quick Start

## Installation

To install the latest release:

```
pip install browser-history
```

To install from the master branch (warning: development version. Things could break)

```
pip install git+https://github.com/pesos/browser-history.git
```

## Usage

### History

To get history from all installed browsers:
```python
from browser_history import get_history

outputs = get_history()

# his is a list of (datetime.datetime, url) tuples
his = outputs.histories
```

If you want history from a specific browser:
```python
from browser_history.browsers import Firefox

f = Firefox()
outputs = f.fetch_history()

# his is a list of (datetime.datetime, url) tuples
his = outputs.histories
```

 - `Firefox` in the above snippet can be replaced with any of the [supported browsers](https://browser-history.readthedocs.io/en/latest/browsers.html).

### Bookmarks

WARNING: Experimental feature. Although this has been confirmed to work on multiple (Firefox and Chromium based) browsers
on all platforms, it is not covered by tests and has not been used as much as the history feature.

To get bookmarks from all installed browsers:
```python
from browser_history import get_bookmarks

outputs = get_bookmarks()

# bms is a list of (datetime.datetime, url, title, folder) tuples
bms = outputs.bookmarks
```

To get bookmarks from a specific browser:
```python
from browser_history.browsers import Firefox

f = Firefox()
outputs = f.fetch_bookmarks()

# bms is a list of (datetime.datetime, url, title, folder) tuples
bms = outputs.bookmarks
```

Check out the [documentation](https://browser-history.readthedocs.io/en/latest/) for more details.

# Supported Browsers

Read the [documentation](https://browser-history.readthedocs.io/en/latest/browsers.html)

# License

Licensed under the [Apache License, Version 2.0 (the "License")](LICENSE)
