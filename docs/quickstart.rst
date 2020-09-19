.. _quick_start:

Quick Start
===========

Installation
------------

::

    pip install browser-history

Get started:

<<<<<<< HEAD
To get history from all installed browsers:
::

    from browser_history.utils import get_history

    outputs = get_history()

    histories = outputs.get()


- ``histories`` is a list of ``(datetime.datetime, url)`` tuples.


If you want history from a specific browser:
=======
>>>>>>> a18905f7a05b23ac3f1bf34369968b51debd585e
::

    from browser_history.browsers import Firefox

    f = Firefox.fetch()

    his = f.get()

- ``Firefox`` in the above snippet can be replaced with any of the :ref:`supported_browsers`.
- ``his`` is a list of ``(datetime.datetime, url)`` tuples from the firefox browser.



<<<<<<< HEAD

Command Line
------------

Running ``browser-history`` in shell/terminal/command prompt will return history from all
browsers with each line in the output containing the timestamp and URL separated by a comma.

To get history from a specific browser::
=======
::

    from browser_history.utils import get_history

    outputs = get_history()

    histories = outputs.get()


- ``histories`` is a list of ``(datetime.datetime, url)`` tuples from every browser installed on the system.
>>>>>>> a18905f7a05b23ac3f1bf34369968b51debd585e

    browser-history -b Firefox

Checkout the :ref:`cli` help page for more information
