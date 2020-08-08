.. _quick_start:

Quick Start
===========

Get started::

    from browser_history import Firefox

    f = Firefox()

    his = f.history()

- ``Firefox`` in the above snippet can be replaced with any of the :ref:`supported_browsers`.
- ``his`` is a list of ``(datetime.datetime, url)`` tuples.


