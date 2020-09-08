.. _quick_start:

Quick Start
===========

Installation::

    pip install browser-history

Get started::

    from browser_history.browsers import Firefox

    f = Firefox()

    his = f.fetch()

- ``Firefox`` in the above snippet can be replaced with any of the :ref:`supported_browsers`.
- ``his`` is a list of ``(datetime.datetime, url)`` tuples.


