.. _cli:

Command Line Interface
======================

This package provides a command line tool named ``browser-history`` that is
automatically added to path when installed through ``pip``.

Help page for the CLI is given below. It can also be accessed using
``browser-history --help``.

CLI Help Page
-------------

.. argparse::
   :module: browser_history.cli
   :func: make_parser
   :prog: browser-history
