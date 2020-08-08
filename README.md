# browser-history

![tests](https://github.com/Samyak2/browser-history/workflows/tests/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/browser-history/badge/?version=latest)](https://browser-history.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/browser-history.svg)](https://badge.fury.io/py/browser-history)

``browser-history`` is a simple, zero-dependencies, developer-friendly python
package to retrieve (almost) any browser's history on (almost) any platform.

# Quick Start

## Installation

`pip install browser-history`

## Usage

```python
from browser_history.browsers import Firefox

f = Firefox()

his = f.history()
```

 - `Firefox` in the above snippet can be replaced with any of the [supported browsers](https://browser-history.readthedocs.io/en/latest/browsers.html).
 - `his` is a list of `(datetime.datetime, url)` tuples.

Check out the [documentation](https://browser-history.readthedocs.io/en/latest/) for more details.

# Supported Browsers

Read the [documentation](https://browser-history.readthedocs.io/en/latest/browsers.html)

# License

Licensed under the [Apache License, Version 2.0 (the "License")](LICENSE)
