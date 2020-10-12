# browser-history

![tests](https://github.com/pesos/browser-history/workflows/tests/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/browser-history/badge/?version=latest)](https://browser-history.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/browser-history.svg)](https://badge.fury.io/py/browser-history)
[![codecov](https://codecov.io/gh/pesos/browser-history/branch/master/graph/badge.svg)](https://codecov.io/gh/pesos/browser-history)

``browser-history`` is a simple, zero-dependencies, developer-friendly python
package to retrieve (almost) any browser's history on (almost) any platform.

# Quick Start

## Installation

`pip install browser-history`

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
