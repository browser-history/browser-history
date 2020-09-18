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

    f = Firefox.fetch()

    histories = f.get()

- ``Firefox`` in the above snippet can be replaced with any of the :ref:`supported_browsers`.
- ``his`` is a list of ``(datetime.datetime, url)`` tuples.

Command Line
------------

Running ``browser-history`` in shell/terminal/command prompt will return history from all
browsers with each line in the output containing the timestamp and URL separated by a comma.

To get history from a specific browser::

    browser-history -b Firefox

Checkout the :ref:`cli` help page for more information
