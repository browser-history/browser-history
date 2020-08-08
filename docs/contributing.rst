Contributing
============

Technicalities
--------------

(might be outdated)

Adding support for a new browser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Browsers are defined in ``browser_history/browsers.py``. To add a new browser, create
a new class extending the :py:class:`browser_history.generic.Browser`.
See :ref:`browser_functionality` for the class variables that must be set and their
description. Currently only browsers which use SQLite databases to store history are
supported.

Adding support for a new platform
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(platform here refers to an OS)

This one is tricky. Platforms are defined in :py:class:`browser_history.utils.Platform`.
To add a new platform, the following must be updated.

* Add the platform to :py:class:`browser_history.utils.Platform`
* Update :py:func:`browser_history.utils.get_platform` to correctly return the
  platform.
* Update the ``__init__`` method of :py:class:`browser_history.generic.Browser`
  and create a new class variable for that platform.
* Update as many :ref:`supported_browsers` as possible with the ``platform_path``
  for the new platform.

Tests
^^^^^

**Test Home directory:**

Tests are done by including a minimal copy of the browser files with the correct paths.
For example, on ``Linux`` platform and for the ``Firefox`` browser,
``tests/test_homedirs/Linux`` contains a minimal snapshot of the home directory with only
the files required for extracting history which is the following for ``Firefox`` on
``Linux``::

    test_homedirs/Linux
    └── .mozilla
        └── firefox
            └── profile
                └── places.sqlite

It would be a great help for us if you contribute any missing platform-browser
combination, even if you don't write any tests accompanying them.

**Writing Tests:**

Tests are executed using `pytest <https://docs.pytest.org/en/stable/>`_.
`Monkeypatching <https://docs.pytest.org/en/stable/monkeypatch.html>`_ is used to change
the home directory to one of the test directories and to emulate the home directory of
a different platform.

The monkeypatches are defined in ``tests/utils.py``. The ``change_homedir`` fixture
must be used for all tests and one of ``become_windows``, ``become_mac`` or
``become_linux``. Look at some tests in ``tests/test_browsers.py`` for examples.

