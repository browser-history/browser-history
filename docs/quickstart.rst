.. _quick_start:

Quick Start
===========

Installation
------------

::

    pip install browser-history

Get started
-----------

::

    from browser_history.browsers import Firefox
    from browser_history.utils import *

    f = Firefox.fetch()

    his = f.get()

    all_browsers = get_history()

    all_histories = all_browsers.get()

- ``Firefox`` in the above snippet can be replaced with any of the :ref:`supported_browsers`.
- ``his`` is a list of ``(datetime.datetime, url)`` tuples from the firefox browser.
- ``all_histories`` is a list of ``(datetime.datetime, url)`` tuples from every browser installed on the system.

Command Line
------------

Running ``browser-history`` in shell/terminal/command prompt will return history from all
browsers with each line in the output containing the timestamp and URL separated by a comma.

To get history from a specific browser::

    browser-history -b Firefox

Checkout the :ref:`cli` help page for more information
