"""
This module defines the generic base class and the functionality.

All browsers from :py:mod:`browser_history.browsers` inherit this class.
"""

import abc
import csv
import datetime
import json
import os
import shutil
import sqlite3
import tempfile
import typing
import warnings
from collections import defaultdict
from functools import partial
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple
from urllib.parse import urlparse

import browser_history.utils as utils

HistoryVar = List[Tuple[datetime.datetime, str]]
BookmarkVar = List[Tuple[datetime.datetime, str, str, str]]


class Browser(abc.ABC):
    """A generic class to support all major browsers with minimal
    configuration.

    Currently, only browsers which save the history in SQLite files are
    supported.

    To create a new browser type, the following class variables must be set.

    * :py:class:`name`
    * **paths**: A path string, relative to the home directory, where the
      browsers data is saved.
      At least one of the following must be set:
      :py:class:`windows_path`, :py:class:`mac_path`, :py:class:`linux_path`
    * :py:class:`history_file`
    * :py:class:`history_SQL`

    These following class variable can optionally be set:

    * :py:class:`bookmarks_file`
    * :py:class:`bookmarks_parser`
    * :py:class:`profile_support`
    * :py:class:`profile_dir_prefixes`
    * :py:class:`_local_tz`
    * :py:class:`aliases`: A tuple containing other names for the browser in lowercase

    :param plat: the current platform. A value of :py:class:`None` means the platform
       will be inferred from the system.

    Examples:

    >>> class CustomBrowser(Browser):
    ...     name = 'custom browser'
    ...     aliases = ('custom-browser', 'customhtm')
    ...     history_file = 'history_file'
    ...     history_SQL = \"\"\"
    ...         SELECT
    ...             url
    ...         FROM
    ...             history_visits
    ...     \"\"\"
    ...     linux_path = 'browser'
    ...
    ... vars(CustomBrowser())
    {'profile_dir_prefixes': [], 'history_dir': PosixPath('/home/username/browser')}
    """

    windows_path: typing.Optional[str] = None  #: browser path on Windows.
    mac_path: typing.Optional[str] = None  #: browser path on Mac OS.
    linux_path: typing.Optional[str] = None  #: browser path on Linux.

    profile_support: bool = False  #: boolean indicating whether
    """Boolean indicating whether the browser supports multiple profiles."""

    profile_dir_prefixes: typing.Optional[typing.List[typing.Any]] = None
    """List of possible prefixes for the profile directories.
    Keep empty to check all subdirectories in the browser path.
    """

    bookmarks_file: typing.Optional[str] = None
    """Name of the (SQLite, JSON or PLIST) file which stores the bookmarks."""

    _local_tz: typing.Optional[datetime.tzinfo] = (
        datetime.datetime.now().astimezone().tzinfo
    )
    """Gets a datetime object of the current time as per the users timezone."""

    history_dir: Path
    """History directory."""

    aliases: tuple = ()
    """Gets possible names (lower-cased) used to refer to the browser type.
    Useful for making the browser detectable as a default browser which may be
    named in various forms on different platforms. Do not include :py:class:`name`
    in this list"""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """A name for the browser. Not used anywhere except for logging and errors."""

    @property
    @abc.abstractmethod
    def history_file(self) -> str:
        """Name of the (SQLite) file which stores the history."""

    @property
    @abc.abstractmethod
    def history_SQL(self) -> str:
        """SQL query required to extract history from the ``history_file``.
        The query must return three columns: ``visit_time``, ``url`` and ``title``.
        The ``visit_time`` must be processed using the `datetime`_
        function with the modifier ``localtime``.

            .. _datetime: https://www.sqlitetutorial.net/sqlite-date-functions/sqlite-datetime-function/
        """  # pylint: disable=line-too-long # noqa: E501

    def __init__(self, plat: typing.Optional[utils.Platform] = None):
        self.profile_dir_prefixes = []
        if plat is None:
            plat = utils.get_platform()
        homedir = Path.home()

        error_string = (
            f"{self.name} browser is not supported on {utils.get_platform_name(plat)}"
        )
        if plat == utils.Platform.WINDOWS:
            assert self.windows_path is not None, error_string
            self.history_dir = homedir / self.windows_path
        elif plat == utils.Platform.MAC:
            assert self.mac_path is not None, error_string
            self.history_dir = homedir / self.mac_path
        elif plat == utils.Platform.LINUX:
            assert self.linux_path is not None, error_string
            self.history_dir = homedir / self.linux_path
        else:
            raise NotImplementedError()

        if self.profile_support and not self.profile_dir_prefixes:
            self.profile_dir_prefixes.append("*")

    def bookmarks_parser(
        self, bookmark_path
    ):  # pylint: disable=assignment-from-no-return
        """A function to parse bookmarks and convert to readable format."""

    def profiles(self, profile_file) -> typing.List[str]:
        """Returns a list of profile directories. If the browser is supported
        on the current
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

    def history_path_profile(self, profile_dir: Path) -> typing.Optional[Path]:
        """Returns path of the history file for the given ``profile_dir``

        The ``profile_dir`` should be one of the outputs from
        :py:meth:`profiles`

        :param profile_dir: Profile directory (should be a single name,
            relative to ``history_dir``)
        :type profile_dir: :py:class:`pathlib.Path`
        :return: path to history file of the profile
        """
        if self.history_file is None:
            return None
        return self.history_dir / profile_dir / self.history_file

    def bookmarks_path_profile(self, profile_dir: Path) -> typing.Optional[Path]:
        """Returns path of the bookmark file for the given ``profile_dir``

        The ``profile_dir`` should be one of the outputs from
        :py:meth:`profiles`

        :param profile_dir: Profile directory (should be a single name,
            relative to ``history_dir``)
        :type profile_dir: :py:class:`pathlib.Path`
        :return: path to bookmark file of the profile
        """
        if self.bookmarks_file is None:
            return None
        return self.history_dir / profile_dir / self.bookmarks_file

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

        :param profile_dirs: List or iterable of profile directories. Can be
            obtained from :py:meth:`profiles`
        :type profile_dirs: list(str)
        :return: Object of class :py:class:`browser_history.generic.Outputs`
            with the data member histories set to
            list(tuple(:py:class:`datetime.datetime`, str))
        :rtype: :py:class:`browser_history.generic.Outputs`
        """
        history_paths = [
            self.history_path_profile(profile_dir) for profile_dir in profile_dirs
        ]
        return self.fetch_history(history_paths)

    def fetch_history(self, history_paths=None, sort=True, desc=False):
        """Returns history of all available profiles stored in SQL.

        The returned datetimes are timezone-aware with the local timezone set
        by default.

        The history files are first copied to a temporary location and then
        queried, this might lead to some additional overhead and results
        returned might not be the latest if the browser is in use. This is
        done because the SQlite files are locked by the browser when in use.

        :param history_paths: (optional) a list of history files.
        :type history_paths: list(:py:class:`pathlib.Path`)
        :param sort: (optional) flag to specify if the output should be
            sorted. Default value set to True.
        :type sort: boolean
        :param desc: (optional)  flag to specify asc/desc
            (Applicable if sort is True) Default value set to False.
        :type asc: boolean
        :return: Object of class :py:class:`browser_history.generic.Outputs`
            with the data member histories set to
            list(tuple(:py:class:`datetime.datetime`, str, str))
            If the browser is not installed, this object will be empty.
        :rtype: :py:class:`browser_history.generic.Outputs`
        """
        if history_paths is None:
            history_paths = self.paths(profile_file=self.history_file)
        output_object = Outputs(fetch_type="history")
        with tempfile.TemporaryDirectory() as tmpdirname:
            for history_path in history_paths:
                if os.path.getsize(history_path.absolute()) == 0:
                    continue
                copied_history_path = shutil.copy2(history_path.absolute(), tmpdirname)
                conn = sqlite3.connect(
                    f"file:{copied_history_path}?mode=ro&immutable=1&nolock=1", uri=True
                )
                cursor = conn.cursor()
                cursor.execute(self.history_SQL)
                date_histories = [
                    (
                        datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S").replace(
                            tzinfo=self._local_tz
                        ),
                        url,
                        title,
                    )
                    for d, url, title in cursor.fetchall()
                ]
                output_object.histories.extend(date_histories)
                if sort:
                    # Can't sort tuples with None values, and some titles
                    # are None, so replace them with ''
                    output_object.histories.sort(
                        key=lambda h: tuple(el or "" for el in h), reverse=desc
                    )
                conn.close()
        return output_object

    def fetch_bookmarks(self, bookmarks_paths=None, sort=True, desc=False):
        """Returns bookmarks of all available profiles stored in SQL or JSON
        or plist.

        The returned datetimes are timezone-aware with the local timezone set
        by default.

        The bookmark files are first copied to a temporary location and then
        queried, this might lead to some additional overhead and results
        returned might not be the latest if the browser is in use. This is
        done because the SQlite files are locked by the browser when in use.

        :param bookmarks_paths: (optional) a list of bookmark files.
        :type bookmarks_paths: list(:py:class:`pathlib.Path`)
        :param sort: (optional) flag to specify if the output should be
            sorted. Default value set to True.
        :type sort: boolean
        :param desc: (optional)  flag to specify asc/desc
            (Applicable if sort is True) Default value set to False.
        :type asc: boolean
        :return: Object of class :py:class:`browser_history.generic.Outputs`
            with the attribute bookmarks set to a list of
            (timestamp, url, title, folder) tuples
        :rtype: :py:class:`browser_history.generic.Outputs`
        """

        assert (
            self.bookmarks_file is not None
        ), "Bookmarks are not supported for {} browser".format(self.name)
        if bookmarks_paths is None:
            bookmarks_paths = self.paths(profile_file=self.bookmarks_file)
        output_object = Outputs(fetch_type="bookmarks")
        with tempfile.TemporaryDirectory() as tmpdirname:
            for bookmarks_path in bookmarks_paths:
                if not os.path.exists(bookmarks_path):
                    continue
                if os.path.getsize(bookmarks_path.absolute()) == 0:
                    continue
                copied_bookmark_path = shutil.copy2(
                    bookmarks_path.absolute(), tmpdirname
                )
                # pylint: disable=assignment-from-no-return
                date_bookmarks = self.bookmarks_parser(copied_bookmark_path)
                output_object.bookmarks.extend(date_bookmarks)
            if sort:
                output_object.bookmarks.sort(reverse=desc)
        return output_object

    @classmethod
    def is_supported(cls):
        """Checks whether the browser is supported on current platform

        :return: True if browser is supported on current platform else False
        :rtype: boolean
        """
        support_check = {
            utils.Platform.LINUX: cls.linux_path,
            utils.Platform.WINDOWS: cls.windows_path,
            utils.Platform.MAC: cls.mac_path,
        }
        return support_check.get(utils.get_platform()) is not None


class Outputs:
    """
    A generic class to encapsulate history and bookmark outputs and to
    easily convert them to JSON, CSV or other formats.

    :param fetch_type: string argument to select history output or bookmarks output
    """

    # type hint for histories and bookmarks have to be manually written for
    # docs instead of using HistoryVar and BookmarkVar respectively
    histories: List[Tuple[datetime.datetime, str, str]]
    """List of tuples of Timestamp, URL, Title."""
    bookmarks: List[Tuple[datetime.datetime, str, str, str]]
    """List of tuples of Timestamp, URL, Title, Folder."""

    _valid_fetch_types = ("history", "bookmarks")

    format_map: Dict[str, Callable]
    """Dictionary which maps output formats to their respective functions."""

    def __init__(self, fetch_type):
        self.fetch_type = fetch_type
        self.histories = []
        self.bookmarks = []
        self.format_map = {
            "csv": self.to_csv,
            "json": self.to_json,
            "jsonl": partial(self.to_json, json_lines=True),
        }

    @property
    def field_map(self) -> typing.Dict[str, typing.Any]:
        """[Deprecated] This was not meant for public usage and will be removed soon.

        Use _get_data and _get_fields if you really need this.
        """
        warnings.warn(
            "Outputs.field_map is deprecated. This property was not "
            + "meant for public usage. Use _get_data and _get_fields "
            + "if you really need this.",
            DeprecationWarning,
        )
        return {
            "history": {"var": self.histories, "fields": ("Timestamp", "URL")},
            "bookmarks": {
                "var": self.bookmarks,
                "fields": ("Timestamp", "URL", "Title", "Folder"),
            },
        }

    def _get_data(self):
        """Return the list of histories or bookmarks (depending on `fetch_type`)."""
        if self.fetch_type == "history":
            return self.histories
        elif self.fetch_type == "bookmarks":
            return self.bookmarks
        else:
            raise ValueError(f"Invalid fetch type {self.fetch_type}")

    def _get_fields(self):
        """Return names of the fields of the data."""
        if self.fetch_type == "history":
            return ("Timestamp", "URL", "Title")
        elif self.fetch_type == "bookmarks":
            return ("Timestamp", "URL", "Title", "Folder")
        else:
            raise ValueError(f"Invalid fetch type {self.fetch_type}")

    def sort_domain(self) -> typing.DefaultDict[Any, List[Any]]:
        """
        Returns the history/bookamarks sorted according to the domain-name.

        Examples:

        >>> from datetime import datetime
        ... from browser_history import generic
        ... entries = [
        ...     (datetime(2020, 1, 1), 'https://google.com', 'Google'),
        ...     (
        ...         datetime(2020, 1, 1),
        ...         "https://google.com/imghp?hl=EN",
        ...         "Google Images",
        ...     ),
        ...     (datetime(2020, 1, 1), 'https://example.com', 'Example'),
        ... ]
        ... obj = generic.Outputs('history')
        ... obj.histories = entries
        ... obj.sort_domain()
        defaultdict(<class 'list'>, {
            'example.com': [
                [
                    datetime.datetime(2020, 1, 1, 0, 0),
                    'https://example.com',
                    'Example'
                ]
            ],
            'google.com': [
                 [
                    datetime.datetime(2020, 1, 1, 0, 0),
                    'https://google.com',
                    'Google'
                 ],
                 [
                    datetime.datetime(2020, 1, 1, 0, 0),
                    'https://google.com/imghp?hl=EN',
                    'Google Images'
                ]
            ]
         })
        """
        domain_histories: typing.DefaultDict[typing.Any, List[Any]] = defaultdict(list)
        for entry in self._get_data():
            domain_histories[urlparse(entry[1]).netloc].append(entry)
        return domain_histories

    def formatted(self, output_format: str = "csv") -> str:
        """
        Returns history or bookmarks as a :py:class:`str` formatted as
        ``output_format``

        :param output_format: One the formats in `csv`, `json`, `jsonl`
        """
        # convert to lower case since the formats tuple is enforced in
        # lowercase
        output_format = output_format.lower()
        if self.format_map.get(output_format):
            # fetch the required formatter and call it. The formatters are
            # instance methods so no need to pass any arguments
            formatter = self.format_map[output_format]
            return formatter()
        raise ValueError(
            f"Invalid format {output_format}. Should be one of \
            {self.format_map.keys()}"
        )

    def to_csv(self) -> str:
        """
        Return history or bookmarks formatted as a comma separated string with
        the first row having the fields names

        :return: string with the output in CSV format

        Examples:

        >>> from datetime import datetime
        ... from browser_history import generic
        ... entries = [
        ...     [datetime(2020, 1, 1), 'https://google.com', 'Google'],
        ...     [datetime(2020, 1, 1), 'https://example.com', 'Example Domain'],
        ... ]
        ... obj = generic.Outputs('history')
        ... obj.histories = entries
        ... print(obj.to_csv())
        Timestamp,URL
        2020-01-01 00:00:00,https://google.com,Google
        2020-01-01 00:00:00,https://example.com,Example Domain

        """
        # we will use csv module and let it do all the heavy lifting such as
        # special character escaping and correct line termination escape
        # sequences
        # The catch is, we need to return a string but the csv module only
        # works with files so we will use StringIO to build the csv in
        # memory first
        with StringIO() as output:
            writer = csv.writer(output)
            writer.writerow(self._get_fields())
            for row in self._get_data():
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
        ...     [datetime(2020, 1, 1), 'https://google.com', 'Google'],
        ...     [datetime(2020, 1, 1), 'https://example.com', 'Example Domain'],
        ... ]
        ... obj = generic.Outputs()
        ... obj.entries = entries
        ... print(obj.to_json(True))
        {
            "Timestamp": "2020-01-01T00:00:00",
            "URL": "https://google.com",
            "Title": "Google",
        }
        {
            "Timestamp": "2020-01-01T00:00:00",
            "URL": "https://example.com",
            "Title": "Example Domain",
        }
        >>> print(obj.to_json())
        {
            "history": [
                {
                    "Timestamp": "2020-01-01T00:00:00",
                    "URL": "https://google.com",
                    "Title", "Google"
                },
                {
                    "Timestamp": "2020-01-01T00:00:00",
                    "URL": "https://example.com",
                    "Title": "Example Domain"
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
                # skip coverage for this line (tested but not detected)
                return super().default(o)  # pragma: no cover

        # fetch lines
        lines = []
        for entry in self._get_data():
            json_record = {}
            for field, value in zip(self._get_fields(), entry):
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
        Saves history or bookmarks to a file. Infers the type from the given
        filename extension. If the type could not be inferred, it defaults
        to csv.

        :param filename: the name of the file.
        :param output_format: (optional)One the formats in `csv`, `json`,
            `jsonl`.
            If not given, it will automatically be inferd from the file's
            extension
        """
        if output_format == "infer":
            output_format = os.path.splitext(filename)[1][1:]
            if output_format not in self.format_map:
                raise ValueError(
                    f"Invalid extension .{output_format}. Should be one of "
                    f"{', '.join(self.format_map.keys())}"
                )

        with open(filename, "w") as out_file:
            out_file.write(self.formatted(output_format))


class ChromiumBasedBrowser(Browser, abc.ABC):
    """A generic class to support the increasing number of Chromium based
    browsers.
    """

    profile_dir_prefixes = ["Default*", "Profile*"]

    history_file = "History"
    bookmarks_file = "Bookmarks"

    history_SQL = """
            SELECT
                datetime(
                    visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime'
                ) as 'visit_time',
                urls.url,
                urls.title
            FROM
                visits INNER JOIN urls ON visits.url = urls.id
            WHERE
                visits.visit_duration > 0
            ORDER BY
                visit_time DESC
        """

    def bookmarks_parser(self, bookmark_path):
        """Returns bookmarks of a single profile for Chrome based browsers
        The returned datetimes are timezone-aware with the local timezone set
        by default

        :param bookmark_path: the path of the bookmark file
        :type bookmark_path: str
        :return: a list of tuples of bookmark information
        :rtype: list(tuple(:py:class:`datetime.datetime`, str, str, str))
        """

        def _deeper(bookmarks_json, folder, bookmarks_list):
            for node in bookmarks_json:
                if node == "children":
                    for child in bookmarks_json[node]:
                        if child["type"] == "url":
                            d_t = datetime.datetime(
                                1601, 1, 1, tzinfo=datetime.timezone.utc
                            ) + datetime.timedelta(
                                microseconds=int(child["date_added"])
                            )
                            bookmarks_list.append(
                                (
                                    d_t.replace(microsecond=0).astimezone(
                                        self._local_tz
                                    ),
                                    child["url"],
                                    child["name"],
                                    folder,
                                )
                            )
                        elif child["type"] == "folder":
                            bookmarks_list = _deeper(
                                child,
                                folder + os.sep + child["name"],
                                bookmarks_list,
                            )
                    break
                else:
                    bookmarks_list = _deeper(
                        bookmarks_json[node], folder, bookmarks_list
                    )
            return bookmarks_list

        with open(bookmark_path, "rb") as b_p:
            b_m = json.load(b_p)
            bookmarks_list = []
            for root in b_m["roots"]:
                if isinstance(b_m["roots"][root], dict):
                    bookmarks_list = _deeper(b_m["roots"][root], root, bookmarks_list)
        return bookmarks_list
