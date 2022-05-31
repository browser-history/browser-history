"""This module defines the base Browser class and related things.

All browsers from :py:mod:`browser_history.browsers` inherit this class.
"""

import abc
import datetime
import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Type, Union, overload
from browser_history.outputs import BookmarksOutputs, HistoryOutputs

import browser_history.utils as utils
from browser_history.exceptions import BookmarksNotSupportedError
from browser_history.utils.timezone import local_tz


class Browser(abc.ABC):
    """A base class to support all major browsers with minimal configuration.

    Currently, only browsers which save the history in SQLite files are
    supported.

    To create a new browser type, the following class variables must be set.

    * :py:class:`name`
    * **paths**: A path string, relative to the home directory, where the
      browsers data is saved.
      At least one of the following must be set:
      :py:class:`_windows_path`, :py:class:`_mac_path`, :py:class:`_linux_path`
    * :py:class:`_history_file`
    * :py:class:`_history_SQL`

    These following class variable can optionally be set:

    * :py:class:`_bookmarks_file`
    * :py:class:`_bookmarks_parser`
    * :py:class:`profile_support`
    * :py:class:`_profile_dir_prefixes`
    * :py:class:`_local_tz`
    * :py:class:`_aliases`: A tuple containing other names for the browser in lowercase

    Example:
        >>> from browser_history.generic import Browser
        >>> class CustomBrowser(Browser):
        ...     name = 'custom browser'
        ...     _aliases = ('custom-browser', 'customhtm')
        ...     _history_file = 'history_file'
        ...     _history_SQL = \"\"\"
        ...         SELECT
        ...             url
        ...         FROM
        ...             history_visits
        ...     \"\"\"
        ...     _linux_path = 'browser'
        ...
        >>> browser = CustomBrowser()
        >>> browser
        <CustomBrowser object at 0x...>
    """

    _windows_path: Optional[str] = None
    """Path to directory where the browser data is stored on Windows."""
    _mac_path: Optional[str] = None
    """Path to directory where the browser data is stored on Mac OS."""
    _linux_path: Optional[str] = None
    """Path to directory where the browser data is stored on Linux."""

    profile_support: bool = False
    """Whether the browser supports multiple profiles."""

    _profile_dir_prefixes: Optional[List[str]] = None
    """List of possible prefixes for the profile directories.

    Keep empty to check all subdirectories in the browser path.
    """

    _bookmarks_file: Optional[str] = None
    """Name of the (SQLite, JSON or PLIST) file which stores the bookmarks."""

    _aliases: tuple = ()
    """Possible names (lower-cased) used to refer to the browser type.

    Useful for making the browser detectable as a default browser which may be
    named in various forms on different platforms. Do not include :py:class:`name`
    in this list"""

    name: str
    """Name of the browser."""

    _history_file: str
    """Name of the (SQLite) file which stores the history."""

    _history_SQL: str
    """The SQL query required to extract history from the ``_history_file``.

    The query must return two columns: ``visit_time`` and ``url``.
    The ``visit_time`` must be processed using the `datetime`_
    function with the modifier ``localtime``.

    .. _datetime: https://www.sqlitetutorial.net/sqlite-date-functions/sqlite-datetime-function/
    """  # pylint: disable=line-too-long # noqa: E501, D401
    # TODO: remove D401 ignore here once
    #       https://github.com/PyCQA/pydocstyle/pull/546
    #       is available

    def __init__(self, plat: Optional[utils.Platform] = None):
        """Initialize a Browser, ready to extract history or bookmarks.

        Args:
            plat: the system platform. Will be inferred if not provided.
        """
        if plat is None:
            plat = utils.get_platform()
        homedir = Path.home()

        self._history_dir: Path
        """:py:class:`Path` to the directory where this browser's history is stored."""

        error_string = (
            f"{self.name} browser is not supported on {utils.get_platform_name(plat)}"
        )
        if plat == utils.Platform.WINDOWS:
            assert self._windows_path is not None, error_string
            self._history_dir = homedir / self._windows_path
        elif plat == utils.Platform.MAC:
            assert self._mac_path is not None, error_string
            self._history_dir = homedir / self._mac_path
        elif plat == utils.Platform.LINUX:
            assert self._linux_path is not None, error_string
            self._history_dir = homedir / self._linux_path
        else:
            raise NotImplementedError()

        if self.profile_support and not self._profile_dir_prefixes:
            self._profile_dir_prefixes = ["*"]

    def _bookmarks_parser(
        self, bookmark_path: str
    ) -> List[Tuple[datetime.datetime, str, str, str]]:
        """Parse bookmarks and convert to a readable format.

        Args:
            bookmark_path: the path of the bookmark file.
        """
        raise NotImplementedError(
            f"Bookmarks not implemented for this browser: {self.name}. "
            f"Got bookmark path: {bookmark_path}"
        )

    def _profiles(self, profile_file: str) -> List[str]:
        """Return a list of profile directories.

        If the browser is supported on the current platform but is not
        installed an empty list will be returned.

        Args:
            profile_file: file to search for in the profile directories.
                This should be either ``_history_file`` or ``_bookmarks_file``.
        """
        if not os.path.exists(self._history_dir):
            utils.logger.info("%s browser is not installed", self.name)
            return []
        if not self.profile_support:
            return ["."]
        profile_dirs = []
        for dirpath, _, filenames in os.walk(str(self._history_dir)):
            for item in filenames:
                # TODO: why join and then split??
                if os.path.split(os.path.join(dirpath, item))[-1] == profile_file:
                    # TODO: why is str(dirpath) needed?
                    path = str(dirpath).split(str(self._history_dir), maxsplit=1)[-1]
                    if path.startswith(os.sep):
                        path = path[1:]
                    if path.endswith(os.sep):
                        path = path[:-1]
                    profile_dirs.append(path)
        return profile_dirs

    def profiles_with_history(self) -> List[str]:
        """All profile names which have browser history."""
        return self._profiles(self._history_file)

    def profiles_with_bookmarks(self) -> List[str]:
        """All profile names which have browser bookmarks."""
        if self._bookmarks_file is None:
            raise BookmarksNotSupportedError(self.name)
        return self._profiles(self._bookmarks_file)

    @overload
    def _history_paths(self, profile_dir: None = None) -> List[Path]:
        ...

    @overload
    def _history_paths(self, profile_dir: str) -> Path:
        ...

    def _history_paths(
        self, profile_dir: Optional[str] = None
    ) -> Union[Path, List[Path]]:
        """Return paths of the history files.

        Args:
            profile_dir: the profile directory. If provided, this should be one of the
                outputs from :py:meth:`profiles_with_history`.

        Returns:
            a single path to the history file if ``profile_dir`` is provided, otherwise
            paths to history files of all profiles.
        """
        if profile_dir is not None:
            return self._history_dir / profile_dir / self._history_file
        else:
            return [
                self._history_dir / profile_dir / self._history_file
                for profile_dir in self._profiles(profile_file=self._history_file)
            ]

    @overload
    def _bookmark_paths(self, profile_dir: None = None) -> List[Path]:
        ...

    @overload
    def _bookmark_paths(self, profile_dir: str) -> Path:
        ...

    def _bookmark_paths(
        self, profile_dir: Optional[str] = None
    ) -> Union[Path, List[Path]]:
        """Return paths of the bookmarks files.

        Args:
            profile_dir: the profile directory. If provided, this should be one of the
                outputs from :py:meth:`profiles_with_bookmarks`.

        Returns:
            a single path to the bookmarks file if ``profile_dir`` is provided,
            otherwise paths to bookmarks files of all profiles.
        """
        if self._bookmarks_file is None:
            raise BookmarksNotSupportedError(self.name)

        if profile_dir is not None:
            return self._history_dir / profile_dir / self._bookmarks_file
        else:
            return [
                self._history_dir / profile_dir / self._bookmarks_file
                for profile_dir in self._profiles(profile_file=self._bookmarks_file)
            ]

    def history_profiles(self, profile_dirs: Sequence[str]) -> HistoryOutputs:
        """Return history of profiles given by `profile_dirs`.

        Args:
            profile_dirs: Profile directories. Can be obtained from
                :py:meth:`_profiles`.
        """
        history_paths = [
            self._history_paths(profile_dir) for profile_dir in profile_dirs
        ]
        return self.fetch_history(history_paths)

    def fetch_history(
        self,
        history_paths: Optional[List[Path]] = None,
        sort=True,
        desc=False,
    ) -> HistoryOutputs:
        """Retrieve browser history.

        The returned datetimes are timezone-aware with the local timezone set
        by default.

        Args:
            history_paths: a list of history files to extract from. The default files
                of all profiles are used if not specified.
            sort: whether the output should be sorted.
            desc: whether the sorting should be in descending order.

        Returns:
            If the browser is not installed, the returned object will be empty.

        Note:
            The history files are first copied to a temporary location and then
            queried, this might lead to some additional overhead and results
            returned might not be the latest if the browser is in use. This is
            done because the SQlite files are locked by the browser when in use.
        """
        # TODO: what does "object will be empty" above mean?
        if history_paths is None:
            history_paths = self._history_paths()
        output_object = HistoryOutputs()
        with tempfile.TemporaryDirectory() as tmpdirname:
            for history_path in history_paths:
                copied_history_path = shutil.copy2(history_path.absolute(), tmpdirname)
                conn = sqlite3.connect(
                    f"file:{copied_history_path}?mode=ro&immutable=1&nolock=1", uri=True
                )
                cursor = conn.cursor()
                cursor.execute(self._history_SQL)
                date_histories = [
                    (
                        datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S").replace(
                            tzinfo=local_tz()
                        ),
                        url,
                    )
                    for d, url in cursor.fetchall()
                ]
                output_object.data.extend(date_histories)
                if sort:
                    output_object.data.sort(reverse=desc)
                conn.close()
        return output_object

    def fetch_bookmarks(
        self,
        bookmarks_paths: Optional[List[Path]] = None,
        sort=True,
        desc=False,
    ) -> BookmarksOutputs:
        """Retrive browser bookmarks.

        The returned datetimes are timezone-aware with the local timezone set
        by default.

        Args:
            history_paths: a list of bookmark files to extract from. The default files
                of all profiles are used if not specified.
            sort: whether the output should be sorted.
            desc: whether the sorting should be in descending order.

        Note:
            The bookmark files are first copied to a temporary location and then
            queried, this might lead to some additional overhead and results
            returned might not be the latest if the browser is in use. This is
            done because the SQlite files are locked by the browser when in use.
        """
        assert (
            self._bookmarks_file is not None
        ), "Bookmarks are not supported for {} browser".format(self.name)
        if bookmarks_paths is None:
            bookmarks_paths = self._bookmark_paths()
        output_object = BookmarksOutputs()
        with tempfile.TemporaryDirectory() as tmpdirname:
            for bookmarks_path in bookmarks_paths:
                if not os.path.exists(bookmarks_path):
                    continue
                copied_bookmark_path = shutil.copy2(
                    bookmarks_path.absolute(), tmpdirname
                )
                date_bookmarks = self._bookmarks_parser(copied_bookmark_path)
                output_object.data.extend(date_bookmarks)
            if sort:
                output_object.data.sort(reverse=desc)
        return output_object

    @classmethod
    def is_supported(cls):
        """Check whether the browser is supported on current platform."""
        support_check = {
            utils.Platform.LINUX: cls._linux_path,
            utils.Platform.WINDOWS: cls._windows_path,
            utils.Platform.MAC: cls._mac_path,
        }
        return support_check.get(utils.get_platform()) is not None

    _implemented_browsers: List[Type["Browser"]] = []
    """A list of Browser subclasses which have been implemented."""

    def __init_subclass__(cls, is_abstract: bool = False, *args, **kwargs):
        """Register list of implemented browsers."""
        super().__init_subclass__(*args, **kwargs)
        if not is_abstract:
            cls._implemented_browsers.append(cls)


class ChromiumBasedBrowser(Browser, is_abstract=True):
    """A base class to support Chromium based browsers."""

    _profile_dir_prefixes = ["Default*", "Profile*"]

    _history_file = "History"
    _bookmarks_file = "Bookmarks"

    _history_SQL = """
        SELECT
            datetime(
                visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime'
            ) as 'visit_time',
            urls.url
        FROM
            visits INNER JOIN urls ON visits.url = urls.id
        WHERE
            visits.visit_duration > 0
        ORDER BY
            visit_time DESC
    """

    def _bookmarks_parser(
        self, bookmark_path: str
    ) -> List[Tuple[datetime.datetime, str, str, str]]:
        """Return bookmarks of a single profile for Chromium based browsers.

        The returned datetimes are timezone-aware with the local timezone set
        by default.

        Args:
            bookmark_path: the path of the bookmark file.
        """
        # TODO: document this
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
                                    d_t.replace(microsecond=0).astimezone(local_tz()),
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

        with open(bookmark_path) as b_p:
            b_m = json.load(b_p)
            bookmarks_list = []
            for root in b_m["roots"]:
                if isinstance(b_m["roots"][root], dict):
                    bookmarks_list = _deeper(b_m["roots"][root], root, bookmarks_list)
        return bookmarks_list
