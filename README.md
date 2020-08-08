# browser-history

![](https://github.com/Samyak2/browser-history/workflows/tests/badge.svg)

A python module to retrieve browser history.

Work in progress.

# Usage

```python
from browser_history,browsers import Firefox

f = Firefox()

his = f.history()
```

 - `Firefox` in the above snippet can be replaced with any of the supported browsers.
 - `his` is a list of `(datetime.datetime, url)` tuples.

# Supported Browsers

## `Firefox`

 - Platforms:
   - Linux
   - Mac OS
   - Windows

## `Chrome`

 - Platforms:
   - Linux
   - Mac OS
   - Windows

## `Chromium`

 - Platforms:
   - Linux

## `Safari`

 - Platforms:
   - Mac OS

# License

Licensed under the [Apache License, Version 2.0 (the "License")](LICENSE)
