Contributing
============

Development Dependencies
------------------------

#. Python 3 (versions 3.6 to 3.8 are currently supported)
#. ``pip install pylint pytest pytest-cov``

    * ``pylint`` to check for errors and to enforce code style.
    * ``pytest`` to run the tests.
    * ``pytest-cov`` to check for code coverage.

#. If you're making changes to the documentation, install the documentation dependencies: ``pip install -r docs/requirements.txt``.

    * Refer `this <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ for a brief introduction to ReST.

Development Process - Short Version
-----------------------------------

#. Select an issue to work on, and inform the maintainers.
#. Fork the repository.
#. ``git clone`` the forked version of the project.
#. Work on the master branch for smaller patches and a separate branch for new features.
#. Make changes, ``git add`` and then commit. Make sure to link the issue number in the commit message.
#. Run the following commands: ``pylint browser_history``, ``pytest --cov=./browser_history``
#. (Optional) If you're updating the documentation, run the following: ``cd docs``, ``make html``
   and then open ``_build/html/index.html`` in a browser to confirm that the documentation rendered correctly.
#. If all tests are passing, pull changes from the original remote with a rebase, and push the changes to your remote repository.
#. Use the GitHub website to create a Pull Request and wait for the maintainers to review it.

Development Process - Long Version
----------------------------------

#. Select an issue to work on, and inform the maintainers.

   * Look for issues, find something that you want to work on.
   * Leave a comment on the issue saying that you want to work on it. The maintainers will give you the go-ahead.

#. Fork the repository.

   * The fork button will be available on the top right in the GitHub website.

#. ``git clone`` the forked version of the project.

   * ``git clone https://github.com/<your-github-username>/browser-history.git``
   * Add a remote to the original repository and name it ``upstream``.
   * ``git remote add upstream https://github.com/pesos/browser-history.git``

#. Work on the master branch for smaller patches and a separate branch for new features.

   * To create a new feature branch and use it, run: ``git checkout -b feature-<feature-name>``.
   * If a feature branch already exists, switch to it before committing: ``git checkout feature-<feature-name>``

#. Make changes, ``git add`` and then commit. Make sure to link the issue number in the commit message.

   * ``git add <names of all modified files>``
   * ``git commit``
   * Make your commit descriptive. The above command will open your text editor.
   * (optional) Tag the commit with appropriate tags such as: (see ``git log`` for examples)

     * ``[CODE]`` - changes to the code
     * ``[FIX]`` - bug fixes
     * ``[TESTS]`` - updates to tests
     * ``[CI]`` - changes related to integrations such as GitHub actions workflows, codecov, etc.
     * ``[DOC]`` - changes to the documentation

   * Continuing the above theme, it is preferred to add changes to a single part in one commit.
     For example, changes to the code, tests and docs for the same feature could go into separate commits.
   * Write the commit message on the first line and a short description about your change. Save and quit the editor to commit your change.

#. Run the following commands:

   * ``pylint browser_history`` - ensure that there are no errors (codes starting with an ``E``).
   * ``pytest --cov=./browser_history`` - ensure that all tests pass.

#. (Optional) If you're updating the documentation, run the following:

   * Change to the docs directory: ``cd docs``
   * Build the documentation: ``make html``
   * Open ``_build/html/index.html`` in a browser to confirm that the documentation rendered correctly.

#. If all tests are passing, pull changes from the original remote with a rebase, and push the changes to your remote repository.

   .. caution:: If you are working on a feature branch, use that branch name instead of master.

   * ``git pull --rebase upstream master``
   * In the extremely small chance that you run into a conflict, just open the files having the conflict and remove the markers and edit the file to the one you want to push. After editing, run ``git rebase --continue`` and repeat till no conflict remains.
   * Verify that your program passes all the tests, and your change actually works in general.

   .. caution:: If you are working on a feature branch, use that branch name instead of master.

   * Push your changes to your fork: ``git push origin master``

#. Use the GitHub website to create a Pull Request and wait for the maintainers to review it.

   * Visit your forked repository and click on "Pull Request". The Pull Request must always be made to the ``pesos/master`` branch.
     Add the relevant description, ensure that you link the original issue.
   * The maintainers will review your code and see if it is okay to merge. It is quite normal for them to suggest you to make some changes in this review.
   * If you are asked to make changes, all you need to do is::

      # make your change
      git add <files that you changed>
      git commit
      git push origin master      # if you are working on a feature branch, use that branch name instead of master

   * The changes are immediately reflected in the pull request. Once the maintainers are satisfied, they will merge your contribution :)

As long as you follow the above instructions things should go well. You are always welcome to ask any questions about the process, or if you face any difficulties in the ``#browser-history-help`` channel on the `PES Open Source Slack <https://pesos.github.io/get-started/communication-channels>`_ .

Release Overview
----------------

(for the more regular contributors)

- ``master`` branch for development. Small patches/enhancements go here.
- ``release`` branch for tagged releases. This is the branch that will be shipped to users.
- Separate ``feature-x`` branches for adding new "big" features. These branches are merged with master, on completion.
- Once we are satisfied with a certain set of features and stability, we pull the changes from master to release. A new release tag is made.

  * The release workflow will automatically submit the release to PyPI. Ensure that version numbers are changed where necessary (``setup.py``, docs, etc.) - PyPI does
    not accept new files for the same version number, once a version is published it cannot be changed.

- If bugs were found on the stable release, we create a hotfix branch and fix the bug. The master branch must also pull the changes from hotfix. A new release tag is created (incrementing with a smaller number).

  * We follow `semantic versioning <https://semver.org/>`_ .

Code of Conduct
---------------

This project follows the `PES Open Source Code of Conduct <https://pesos.github.io/coc>`_ .

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
