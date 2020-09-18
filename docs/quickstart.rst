.. _quick_start:

Quick Start
===========

Installation::

    pip install browser-history

Get started:

::

    from browser_history.browsers import Firefox

    f = Firefox.fetch()

    his = f.get()

- ``Firefox`` in the above snippet can be replaced with any of the :ref:`supported_browsers`.
- ``his`` is a list of ``(datetime.datetime, url)`` tuples from the firefox browser.



::

    from browser_history.utils import get_history

    outputs = get_history()

    histories = outputs.get()


- ``histories`` is a list of ``(datetime.datetime, url)`` tuples from every browser installed on the system.


