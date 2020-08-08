from pathlib import Path
import sqlite3
import tempfile
import shutil
import typing
import datetime

import browser_history.utils as utils

_local_tz = datetime.datetime.now().astimezone().tzinfo

class Browser():
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
    * **history_SQL**: SQL query required to extract history from the ``history_file``. The
      query must return two columns: ``visit_time`` and ``url``. The ``visit_time`` must be
      processed using the
      `datetime <https://www.sqlitetutorial.net/sqlite-date-functions/sqlite-datetime-function/>`_
      function with the modifier ``localtime``.

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

    history_SQL = None

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

    def profiles(self) -> typing.List[str]:
        """Returns a list of profile directories

        (TODO: fix this)
        The returned profiles include only the final name in the path.

        :rtype: list(str)
        """
        if not self.profile_support:
            return ['.']
        maybe_profile_dirs = []
        for profile_dir_prefix in self.profile_dir_prefixes:
            maybe_profile_dirs.extend(self.history_dir.glob(profile_dir_prefix))
        profile_dirs = [profile_dir.name for profile_dir in maybe_profile_dirs
                        if (profile_dir / self.history_file).exists()]

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

    def history_paths(self):
        """Returns a list of history file paths, for all profiles.

        :rtype: list(:py:class:`pathlib.Path`)
        """
        return [self.history_dir / profile_dir / self.history_file
                for profile_dir in self.profiles()]

    def history_profiles(self, profile_dirs):
        """Returns history of profiles given by `profile_dirs`.

        :param profile_dirs: List or iterable of profile directories. Can be obtained from
            :py:meth:`profiles`
        :type profile_dirs: list(str)
        :return: History of selected profiles
        :rtype: list(tuple(:py:class:`datetime.datetime`, str))
        """
        history_paths = [self.history_path_profile(profile_dir) for profile_dir in profile_dirs]
        return self.history(history_paths)

    def history(self, history_paths=None):
        """Returns history of all available profiles.

        The returned datetimes are timezone-aware with the local timezone set by default.

        The history files are first copied to a temporary location and then queried, this might
        lead to some additional overhead and results returned might not be the latest if the
        browser is in use. This is done because the SQlite files are locked by the browser when
        in use.

        :param history_paths: (optional) a list of history files.
        :type history_paths: list(:py:class:`pathlib.Path`)
        :return: List of tuples of a timestamp and corresponding URL
        :rtype: list(tuple(:py:class:`datetime.datetime`, str))
        """
        if history_paths is None:
            history_paths = self.history_paths()
        histories = []
        with tempfile.TemporaryDirectory() as tmpdirname:
            for history_path in history_paths:
                copied_history_path = shutil.copy2(history_path.absolute(), tmpdirname)
                conn = sqlite3.connect(f'file:{copied_history_path}?mode=ro', uri=True)
                cursor = conn.cursor()
                cursor.execute(self.history_SQL)
                date_histories = [(datetime.datetime
                                   .strptime(d, '%Y-%m-%d %H:%M:%S')
                                   .replace(tzinfo=_local_tz), url)
                                  for d, url in cursor.fetchall()]
                histories.extend(date_histories)
                conn.close()
        return histories
