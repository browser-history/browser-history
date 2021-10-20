.. _usage:


*****
Usage
*****

This section details all the uses of ``browser-history`` with complete code examples for each.
Refer the :ref:`quick_start` for basic usage.

Using the API
=============

``browser-history`` has an `API <https://en.wikipedia.org/wiki/API#Libraries_and_frameworks>`_
that allows you to extract history and bookmarks through python code, perhaps in other python programs.

.. _history-usage:

History
-------

The main use case of ``browser-history`` is to extract browsing history from various browsers installed on the system.

History from all browsers
^^^^^^^^^^^^^^^^^^^^^^^^^

To get consolidated history from all browsers:
::

    from browser_history import get_history

    outputs = get_history()

    # his is a list of (datetime.datetime, url) tuples
    his = outputs.histories

History from the default browser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
    Experimental feature. This only works on Linux and Windows, but not for every browser. (see `this PR <https://github.com/pesos/browser-history/pull/123>`_ to check browser and platform support)

Let ``browser-history`` automatically detect the default browser set in the system:
::

    from browser_history.utils import default_browser

    BrowserClass = default_browser()

    if BrowserClass is None:
        # default browser could not be identified
        print("could not get default browser!")
    else:
        b = BrowserClass()
        # his is a list of (datetime.datetime, url) tuples
        his = b.fetch_history().histories

History from a specific browser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need histories from a specific browser:
::

    from browser_history.browsers import Firefox

    f = Firefox()
    outputs = f.fetch_history()

    # his is a list of (datetime.datetime, url) tuples
    his = outputs.histories

``Firefox`` in the above snippet can be replaced with any of the :ref:`supported_browsers`.


History from a specific profile of a browser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``browser-history`` can also extract history from one particular profile of a browser. The profile directory is usually quite different across different systems, this workflow is better suited for the command line tool.

Example:
::

    from browser_history.browsers import Firefox

    b = Firefox()

    # this gives a list of all available profile names
    profiles_available = b.profiles(b.history_file)

    # use the history_profiles function to get histories
    # it needs a list of profile names to use
    outputs = b.history_profiles([profiles_available[0]])

    his = outputs.histories


Save histories to a file
^^^^^^^^^^^^^^^^^^^^^^^^

Use ``outputs.save("filename.ext")`` to save histories to a file (``outputs`` is obtained from ``fetch_history`` as shown in the previous examples). ``ext`` should be one of the supported extensions (``csv``, ``json``, ``jsonl``, etc.). See :py:meth:`~browser_history.generic.Outputs.save` for the list of all supported extensions.

Example:
::

    from browser_history import get_history

    outputs = get_history()

    # save as CSV
    outputs.save("history.csv")
    # save as JSON
    outputs.save("history.json")
    # override format
    outputs.save("history_file", output_format="json")

To see most visited site using bar graph
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This code shows another usages of ``browser-history``. Here history data is fetched from the browser and shown the frequency of visits.
To plot the the graph ``matplotlib`` is used. So, to install matplotlib enter ``pip install matplotlib``.

::

    from browser_history.browsers import get_history
    import matplotlib.pyplot as plt

    def getMostVisitedSites(history):
        frequency = {}
        for tup in history:

            url = tup[1]
            por = url.split("/")
            for idx in range(2, len(por)):
                if len(por[idx])>1:
                    site = por[idx]
                    break
                    
            if site not in frequency:
                frequency[site] += 1
            else:
                frequency[site] = 1

        return frequency

    def showGraph(data):
        sites = list(data.keys())
        visits = list(data.values())
        left = [i for i in range(1, len(visits)+1)]

        plt.bar(left, visits, tick_label = sites)
        plt.ylabel('No. of visits')
        plt.xlabel('sites')
        plt.title('Site visit stats')
        plt.show()

    output = get_history()
    his = output.histories

    rec = getMostVisitedSites(his)
    showGraph(rec)



Bookmarks
---------

.. warning::
    Experimental feature. Although this has been confirmed to work on multiple (Firefox and Chromium based) browsers
    on all platforms, it is has not been tested as much as the history feature.

``browser-history`` also supports extracting bookmarks from some browsers.

All of the usage is similar to extracting history (including saving to a file). You can use the same code examples from :ref:`history-usage` with the following changes:

#. Replace ``fetch_history`` with ``fetch_bookmarks`` (and ``get_history`` with ``get_bookmarks``)

#. Replace ``outputs.histories`` with ``outputs.bookmarks``

Bookmarks (from ``outputs.bookmarks``) are a list of ``(datetime.datetime, url, title, folder)`` tuples.

Using the CLI
=============

``browser-history`` provides a command-line interface that can be accessed by typing ``browser-history`` in a terminal (in Windows, this will be the CMD command prompt or powershell).

The CLI provides all of the functionality of ``browser-history`` (please `open an issue <https://github.com/pesos/browser-history/issues>`_ if any feature is missing from the CLI).

More information about the CLI here: :ref:`cli`.
