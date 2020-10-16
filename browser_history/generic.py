"""
This module defines the generic base class and the functionaliity.

All browsers from :py:mod:`browser_history.browsers` inherit this class.
"""
import csv
import datetime
import json
import os
import shutil
import sqlite3
import tempfile
import typing
from collections import defaultdict
from functools import partial
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Union
from urllib.parse import urlparse

import browser_history.utils as utils

HistoryVar = List[Tuple[datetime.datetime, str]]
BookmarkVar = List[Tuple[datetime.datetime, str, str, str]]


class Browser:
    """A generic class to support all major browsers with minimal configuration.

    Currently, only browsers which save the history in SQLite files are supported.

    To create a new browser type, the following class variables must be set.

    * **name**: A name for the browser. Not used anywhere except for logging and errors.
    * *Paths*: A path string, relative to the home directory, where the browsers data is saved.
      This path should be one level above the profile directories if they exist. At least one
      of the following must be set.

        * **windows_path**: browser path on Windows.
        * **mac_path**: browser path on Mac OS
        * **linux_path**: browser path on Linux

    * **profile_support**: (optional) boolean indicating whether
      the browser supports multiple profiles.
    * **profile_dir_prefixes**: (optional) list of possible prefixes for the
      profile directories. Keep empty to check all subdirectories in the browser path.
    * **history_file**: name of the (SQLite) file which stores the history.
    * **bookmarks_file**: name of the (SQLite, JSON or PLIST) file which stores the bookmarks
    * **history_SQL**: SQL query required to extract history from the ``history_file``. The
      query must return two columns: ``visit_time`` and ``url``. The ``visit_time`` must be
      processed using the
      `datetime <https://www.sqlitetutorial.net/sqlite-date-functions/sqlite-datetime-function/>`_
      function with the modifier ``localtime``.
    * **bookmarks_parser**: a function to parse bookmarks and convert to readable format
    * **_local_tz**: gets a datetime object of the current time as per the users timezone

    :param plat: the current platform. A value of ``None`` means the platform will be
                    inferred from the system.
    :type plat: :py:class:`browser_history.utils.Platform`
    """

    name = "Generic"

    windows_path = None
    mac_path = None
    linux_path = None

    profile_support = False
    profile_dir_prefixes = []

    history_file = None
    bookmarks_file = None

    history_SQL = None

    bookmarks_parser = lambda bookmark_path: None

    _local_tz = datetime.datetime.now().astimezone().tzinfo

    def __init__(self, plat: utils.Platform = None):
        if plat is None:
            plat = utils.get_platform()
        homedir = Path.home()

        error_string = self.name + " browser is not supported on {}"
        if plat == utils.Platform.WINDOWS:
            assert self.windows_path is not None, error_string.format("windows")
            self.history_dir = homedir / self.windows_path
        elif plat == utils.Platform.MAC:
            assert self.mac_path is not None, error_string.format("Mac OS")
            self.history_dir = homedir / self.mac_path
        elif plat == utils.Platform.LINUX:
            assert self.linux_path is not None, error_string.format("Linux")
            self.history_dir = homedir / self.linux_path
        else:
            self.history_dir = None

        if self.profile_support and not self.profile_dir_prefixes:
            self.profile_dir_prefixes.append("*")

    def profiles(self, profile_file) -> typing.List[str]:
        """Returns a list of profile directories. If the browser is supported on the current
        platform but is not installed an empty list will be returned

        :param profile_file: file to search for in the profile directories.
            This should be either ``history_file`` or ``bookmarks_file``.
        :type profile_file: str
        :rtype: list(str)

        """

        if not os.path.exists(self.history_dir):
            utils.logger.info("%s browser is not installed", self.name)
            return []
        if not self.profile_support:
            return ["."]
        profile_dirs = []
        for files in os.walk(str(self.history_dir)):
            for item in files[2]:
                if os.path.split(os.path.join(files[0], item))[-1] == profile_file:
                    path = str(files[0]).split(str(self.history_dir), maxsplit=1)[-1]
                    if path.startswith(os.sep):
                        path = path[1:]
                    if path.endswith(os.sep):
                        path = path[:-1]
                    profile_dirs.append(path)
        return profile_dirs

    def history_path_profile(self, profile_dir: Path) -> Path:
        """Returns path of the history file for the given ``profile_dir``

        The ``profile_dir`` should be one of the outputs from :py:meth:`profiles`

        :param profile_dir: Profile directory (should be a single name, relative to ``history_dir``)
        :type profile_dir: :py:class:`pathlib.Path`
        :return: path to history file of the profile
        :rtype: :py:class:`pathlib.Path`
        """
        return self.history_dir / profile_dir / self.history_file

    def paths(self, profile_file):
        """Returns a list of file paths, for all profiles.

        :rtype: list(:py:class:`pathlib.Path`)
        """
        return [
            self.history_dir / profile_dir / profile_file
            for profile_dir in self.profiles(profile_file=profile_file)
        ]

    def history_profiles(self, profile_dirs):
        """Returns history of profiles given by `profile_dirs`.

        :param profile_dirs: List or iterable of profile directories. Can be obtained from
            :py:meth:`profiles`
        :type profile_dirs: list(str)
        :return: Object of class :py:class:`browser_history.generic.Outputs` with the
            data member histories set to list(tuple(:py:class:`datetime.datetime`, str))
        :rtype: :py:class:`browser_history.generic.Outputs`
        """
        history_paths = [
            self.history_path_profile(profile_dir) for profile_dir in profile_dirs
        ]
        return self.fetch_history(history_paths)

    def fetch_history(self, history_paths=None, sort=True, desc=False):
        """Returns history of all available profiles stored in SQL.

        The returned datetimes are timezone-aware with the local timezone set by default.

        The history files are first copied to a temporary location and then queried, this might
        lead to some additional overhead and results returned might not be the latest if the
        browser is in use. This is done because the SQlite files are locked by the browser when
        in use.

        :param history_paths: (optional) a list of history files.
        :type history_paths: list(:py:class:`pathlib.Path`)
        :param sort: (optional) flag to specify if the output should be sorted.
            Default value set to True.
        :type sort: boolean
        :param desc: (optional)  flag to speicify asc/desc (Applicable iff sort is True)
            Default value set to False.
        :type asc: boolean
        :return: Object of class :py:class:`browser_history.generic.Outputs` with the
            data member histories set to list(tuple(:py:class:`datetime.datetime`, str)).
            If the browser is not installed, this object will be empty.
        :rtype: :py:class:`browser_history.generic.Outputs`
        """
        if history_paths is None:
            history_paths = self.paths(profile_file=self.history_file)
        output_object = Outputs(fetch_type="history")
        with tempfile.TemporaryDirectory() as tmpdirname:
            for history_path in history_paths:
                copied_history_path = shutil.copy2(history_path.absolute(), tmpdirname)
                conn = sqlite3.connect(f"file:{copied_history_path}?mode=ro", uri=True)
                cursor = conn.cursor()
                cursor.execute(self.history_SQL)
                date_histories = [
                    (
                        datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S").replace(
                            tzinfo=self._local_tz
                        ),
                        url,
                    )
                    for d, url in cursor.fetchall()
                ]
                output_object.histories.extend(date_histories)
                if sort:
                    output_object.histories.sort(reverse=desc)
                conn.close()
        return output_object

    def fetch_bookmarks(self, bookmarks_paths=None, sort=True, desc=False):
        """Returns bookmarks of all available profiles stored in SQL or JSON or plist.

        The returned datetimes are timezone-aware with the local timezone set by default.

        The bookmark files are first copied to a temporary location and then queried, this might
        lead to some additional overhead and results returned might not be the latest if the
        browser is in use. This is done because the SQlite files are locked by the browser when
        in use.

        :param bookmarks_paths: (optional) a list of bookmark files.
        :type bookmarks_paths: list(:py:class:`pathlib.Path`)
        :param sort: (optional) flag to specify if the output should be sorted.
            Default value set to True.
        :type sort: boolean
        :param desc: (optional)  flag to speicify asc/desc (Applicable iff sort is True)
            Default value set to False.
        :type asc: boolean
        :return: Object of class :py:class:`browser_history.generic.Outputs` with the
            attribute bookmarks set to a list of (timestamp, url, title, folder) tuples
        :rtype: :py:class:`browser_history.generic.Outputs`
        """

        if bookmarks_paths is None:
            bookmarks_paths = self.paths(profile_file=self.bookmarks_file)
        output_object = Outputs(fetch_type="bookmarks")
        with tempfile.TemporaryDirectory() as tmpdirname:
            for bookmarks_path in bookmarks_paths:
                if not os.path.exists(bookmarks_path):
                    continue
                copied_bookmark_path = shutil.copy2(
                    bookmarks_path.absolute(), tmpdirname
                )
                date_bookmarks = self.bookmarks_parser(copied_bookmark_path)
                output_object.bookmarks.extend(date_bookmarks)
            if sort:
                output_object.bookmarks.sort(reverse=desc)
        return output_object


class Outputs:
    """
    A generic class to encapsulate history and bookmark outputs and to
    easily convert them to JSON, CSV or other formats.

    :param fetch_type: string argument to select history output or bookmarks output
    """

    # type hint for histories and bookmarks have to be manually written for docs
    # instead of using HistoryVar and BookmarkVar respectively
    histories: List[Tuple[datetime.datetime, str]]  #: List of tuples of Timestamp & URL
    bookmarks: List[Tuple[datetime.datetime, str, str, str]]
    """List of tuples of Timestamp, URL, Title, Folder."""

    field_map: Dict[str, Dict[str, Any]]
    """Dictionary which maps fetch_type to the respective variables and formatting fields."""

    format_map: Dict[str, Callable]
    """Dictionary which maps output formats to their respective functions."""

    def __init__(self, fetch_type):
        self.fetch_type = fetch_type
        self.histories = []
        self.bookmarks = []
        self.field_map = {
            "history": {"var": self.histories, "fields": ("Timestamp", "URL")},
            "bookmarks": {
                "var": self.bookmarks,
                "fields": ("Timestamp", "URL", "Title", "Folder"),
            },
        }
        self.format_map = {
            "csv": self.to_csv,
            "json": self.to_json,
            "jsonl": partial(self.to_json, json_lines=True),
        }

    def sort_domain(self) -> Union[HistoryVar, BookmarkVar]:
        """
        Returns the history/bookamarks sorted according to the domain-name.

        Examples:

        >>> from datetime import datetime
        ... from browser_history import generic
        ... entries = [
        ...     [datetime(2020, 1, 1), 'https://google.com'],
        ...     [datetime(2020, 1, 1), 'https://google.com/imghp?hl=EN'],
        ...     [datetime(2020, 1, 1), 'https://example.com'],
        ... ]
        ... obj = generic.Outputs('history')
        ... obj.histories = entries
        ... obj.sort_domain()
        defaultdict(<class 'list'>, {
            'example.com': [[datetime.datetime(2020, 1, 1, 0, 0), 'https://example.com']],
            'google.com': [
                 [datetime.datetime(2020, 1, 1, 0, 0), 'https://google.com'],
                 [datetime.datetime(2020, 1, 1, 0, 0), 'https://google.com/imghp?hl=EN']]
         })
        """
        domain_histories = defaultdict(list)
        for entry in self.field_map[self.fetch_type]["var"]:
            domain_histories[urlparse(entry[1]).netloc].append(entry)
        return domain_histories

    def formatted(self, output_format: str = "csv") -> str:
        """
        Returns history or bookmarks as a :py:class:`str` formatted  as ``output_format``

        :param output_format: One the formats in `csv`, `json`, `jsonl`
        """
        # convert to lower case since the formats tuple is enforced in lowercase
        output_format = output_format.lower()
        if self.format_map.get(output_format):
            # fetch the required formatter and call it. The formatters are instance methods
            # so no need to pass any arguments
            formatter = self.format_map[output_format]
            return formatter()
        raise ValueError(
            f"Invalid format {output_format}. Should be one of \
            {self.format_map.keys()}"
        )

    def to_csv(self) -> str:
        """
        Return history or bookmarks formatted as a comma separated string with the first row
        having the fields names

        :return: string with the output in CSV format

        Examples:

        >>> from datetime import datetime
        ... from browser_history import generic
        ... entries = [
        ...     [datetime(2020, 1, 1), 'https://google.com'],
        ...     [datetime(2020, 1, 1), 'https://example.com'],
        ... ]
        ... obj = generic.Outputs('history')
        ... obj.histories = entries
        ... print(obj.to_csv())
        Timestamp,URL
        2020-01-01 00:00:00,https://google.com
        2020-01-01 00:00:00,https://example.com

        """
        # we will use csv module and let it do all the heavy lifting such as special character
        # escaping and correct line termination escape sequences
        # The catch is, we need to return a string but the csv module only works with files so we
        # will use StringIO to build the csv in memory first
        with StringIO() as output:
            writer = csv.writer(output)
            writer.writerow(self.field_map[self.fetch_type]["fields"])
            for row in self.field_map[self.fetch_type]["var"]:
                writer.writerow(row)
            return output.getvalue()

    def to_json(self, json_lines: bool = False) -> str:
        """
        Return history or bookmarks formatted as a JSON or JSON Lines format
        names. If ``json_lines`` flag is `True` convert to JSON Lines format,
        otherwise convert it to Plain JSON format.

        :param json_lines: flag to specify if the json_string should be JSON Lines.
        :return: string with the output in JSON/JSONL format

        Examples:

        >>> from datetime import datetime
        ... from browser_history import generic
        ... entries = [
        ...     [datetime(2020, 1, 1), 'https://google.com'],
        ...     [datetime(2020, 1, 1), 'https://example.com'],
        ... ]
        ... obj = generic.Outputs()
        ... obj.entries = entries
        ... print(obj.to_json(True))
        {"Timestamp": "2020-01-01T00:00:00", "URL": "https://google.com"}
        {"Timestamp": "2020-01-01T00:00:00", "URL": "https://example.com"}
        >>> print(obj.to_json())
        {
            "history": [
                {
                    "Timestamp": "2020-01-01T00:00:00",
                    "URL": "https://google.com"
                },
                {
                    "Timestamp": "2020-01-01T00:00:00",
                    "URL": "https://example.com"
                }
            ]
        }
        """
        # custom json encoder for datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            """Custom JSON encoder to encode datetime objects"""

            # Override the default method
            def default(self, o):
                if isinstance(o, (datetime.date, datetime.datetime)):
                    return o.isoformat()
                return super().default(o)

        # fetch lines
        lines = []
        for entry in self.field_map[self.fetch_type]["var"]:
            json_record = {}
            for field, value in zip(self.field_map[self.fetch_type]["fields"], entry):
                json_record[field] = value
            lines.append(json_record)

        if json_lines:
            json_string = "\n".join(
                [json.dumps(line, cls=DateTimeEncoder) for line in lines]
            )
        else:
            json_string = json.dumps(
                {self.fetch_type: lines}, cls=DateTimeEncoder, indent=4
            )

        return json_string

    def save(self, filename, output_format="infer"):
        """
        Saves history or bookmarks to a file. Infers the type from the given filename
        extension. If the type could not be inferred, it defaults to csv.

        :param filename: the name of the file.
        :param output_format: (optional)One the formats in `csv`, `json`, `jsonl`.
            If not given, it will automatically be inferd from the file's extension
        """
        if output_format == "infer":
            output_format = os.path.splitext(filename)[1][1:]
            if  not output_format in self.format_map:
                raise ValueError(
                    f"Invalid extension .{output_format}. Should be one of "
                    f"{', '.join(self.format_map.keys())}"
                )

        with open(filename, "w") as out_file:
            out_file.write(self.formatted(output_format))
