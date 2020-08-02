from pathlib import Path
import sqlite3
import tempfile
import shutil
from datetime import datetime

import browser_history.utils as utils

class Browser():
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

    def profiles(self):
        if not self.profile_support:
            return ['.']
        maybe_profile_dirs = []
        for profile_dir_prefix in self.profile_dir_prefixes:
            maybe_profile_dirs.extend(self.history_dir.glob(profile_dir_prefix))
        profile_dirs = [profile_dir for profile_dir in maybe_profile_dirs
                        if (profile_dir / self.history_file).exists()]

        return profile_dirs

    def history_path_profile(self, profile_dir):
        return self.history_dir / profile_dir / self.history_file

    def history_paths(self):
        return [self.history_dir / profile_dir / self.history_file
                for profile_dir in self.profiles()]

    def history_profiles(self, profile_dirs):
        history_paths = [self.history_path_profile(profile_dir) for profile_dir in profile_dirs]
        return self.history(history_paths)

    def history(self, history_paths=None):
        if history_paths is None:
            history_paths = self.history_paths()
        histories = []
        with tempfile.TemporaryDirectory() as tmpdirname:
            for history_path in history_paths:
                copied_history_path = shutil.copy2(history_path.absolute(), tmpdirname)
                conn = sqlite3.connect(f'file:{copied_history_path}?mode=ro', uri=True)
                cursor = conn.cursor()
                cursor.execute(self.history_SQL)
                date_histories = [(datetime.strptime(d, '%Y-%m-%d %H:%M:%S'), url)
                                  for d, url in cursor.fetchall()]
                histories.extend(date_histories)
        return histories
