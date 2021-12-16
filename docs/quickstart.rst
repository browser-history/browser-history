.. _quick_start:

Quick Start
===========

Installation
------------

To install the latest release::

    pip install browser-history

To install from the master branch (warning: development version. Things could break)::

    pip install git+https://github.com/browser-history/browser-history.git


Get started
-----------

History
^^^^^^^

To get history from all installed browsers:
::

    from browser_history import get_history

    outputs = get_history()

    # his is a list of (datetime.datetime, url) tuples
    his = outputs.histories

If you want history from a specific browser:
::

    from browser_history.browsers import Firefox

    f = Firefox()
    outputs = f.fetch_history()

    # his is a list of (datetime.datetime, url) tuples
    his = outputs.histories

- ``Firefox`` in the above snippet can be replaced with any of the :ref:`supported_browsers`.

Bookmarks
^^^^^^^^^

.. warning::
    Experimental feature. Although this has been confirmed to work on multiple (Firefox and Chromium based) browsers
    on all platforms, it has not been tested as much as the history feature.

To get bookmarks from all installed browsers:
::

    from browser_history import get_bookmarks

    outputs = get_bookmarks()

    # bms is a list of (datetime.datetime, url, title, folder) tuples
    bms = outputs.bookmarks

To get bookmarks from a specific browser:
::

    from browser_history.browsers import Firefox

    f = Firefox()
    outputs = f.fetch_bookmarks()

    # bms is a list of (datetime.datetime, url, title, folder) tuples
    bms = outputs.bookmarks

Command Line
------------

Running ``browser-history`` in shell/terminal/command prompt will return history from all
browsers with each line in the output containing the timestamp and URL separated by a comma.

To get history from a specific browser::

    browser-history -b Firefox

Checkout the :ref:`cli` help page for more information
