"""This module defines all supported browsers and their functionality.

All browsers must inherit from :py:mod:`browser_history.generic.Browser`.
"""
import datetime
import json
import os
import sqlite3
from browser_history.generic import Browser
import browser_history.utils as utils

try:
    EXC = None
    if utils.get_platform() == utils.Platform.WINDOWS:
        import win32crypt
    else:
        import keyring
        from pbkdf2 import PBKDF2

        if utils.get_platform() == utils.Platform.LINUX:
            import pyaes
            import gi

            gi.require_version("Secret", "1")
            from gi.repository import Secret
except ImportError as i_exc:
    EXC = i_exc


class Chrome(Browser):
    """Google Chrome Browser

    Supported platforms:

    * Windows
    * Linux
    * Mac OS

    Profile support: Yes
    """

    name = "Chrome"

    windows_path = "AppData/Local/Google/Chrome/User Data"
    mac_path = "Library/Application Support/Google/Chrome/"
    linux_path = ".config/google-chrome"

    profile_support = True
    profile_dir_prefixes = ["Default*", "Profile*"]

    history_file = "History"
    bookmarks_file = "Bookmarks"
    cookies_file = "Cookies"

    history_SQL = """
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
    cookies_SQL = """
            SELECT
                name, host_key, path, encrypted_value, value,
                datetime(
                    expires_utc/1000000-11644473600, 'unixepoch', 'localtime'
                ) as 'expiry_date',
                is_secure, is_httponly
            FROM
                cookies
        """

    def bookmarks_parser(self, bookmark_path):
        """Returns bookmarks of a single profile for Chrome based browsers
        The returned datetimes are timezone-aware with the local timezone set
        by default

        :param bookmark_path : the path of the bookmark file
        :type bookmark_path : str
        :return a list of tuples of bookmark information
        :rtype: list(tuple(:py:class:`datetime.datetime`, str, str, str))
        """

        def _deeper(array, folder, bookmarks_list):
            for node in array:
                if node["type"] == "url":
                    d_t = datetime.datetime(1601, 1, 1) + datetime.timedelta(
                        microseconds=int(node["date_added"])
                    )
                    bookmarks_list.append(
                        (
                            d_t.replace(microsecond=0, tzinfo=self._local_tz),
                            node["url"],
                            node["name"],
                            folder,
                        )
                    )
                else:
                    bookmarks_list = _deeper(
                        node["children"],
                        folder + os.sep + node["name"],
                        bookmarks_list,
                    )
            return bookmarks_list

        with open(bookmark_path) as b_p:
            b_m = json.load(b_p)
            bookmarks_list = []
            for root in b_m["roots"]:
                if isinstance(b_m["roots"][root], dict):
                    bookmarks_list = _deeper(
                        b_m["roots"][root]["children"], root, bookmarks_list
                    )
        return bookmarks_list

    def cookies_parser(self, cookie):

        """Returns cookies of a single input for Chrome based browsers
        The returned datetimes are timezone-aware with the local timezone set
        by default

        :param cookie : dictionary containing cookie details
        :type cookie : dict
        :return a tuple of cookie information
        :rtype: list(tuple(:py:class: str, str, `datetime.datetime`, str, str, str))
        """
        platform = utils.get_platform()
        if EXC is not None:
            logger_map = {
                utils.Platform.LINUX: "'keyring', 'pbkdf2', 'pyaes', 'gi'. ",
                utils.Platform.WINDOWS: "win32crypt. ",
                utils.Platform.MAC: "'keyring', 'pbkdf2'. ",
            }
            utils.logger.info(
                "%s",
                "Module Not Found: "
                + "The following packages are required for retrieving"
                + " cookies on Chrome-based browsers:"
                + logger_map[platform],
            )
            raise ModuleNotFoundError(EXC)
        if platform != utils.Platform.WINDOWS:
            if platform == utils.Platform.LINUX:
                my_pass = None
                flags = Secret.ServiceFlags.LOAD_COLLECTIONS
                service = Secret.Service.get_sync(flags)
                gnome_keyring = service.get_collections()
                unlocked_keyrings = service.unlock_sync(gnome_keyring).unlocked
                keyring_name = "{} Safe Storage".format(self.name.capitalize())
                for unlocked_keyring in unlocked_keyrings:
                    for item in unlocked_keyring.get_items():
                        if item.get_label() == keyring_name:
                            item.load_secret_sync()
                            my_pass = item.get_secret().get_text()
                            break
                        if my_pass:
                            break
                if not my_pass:
                    my_pass = my_pass = keyring.get_password(
                        "{} Keys".format(self.name), "{} Safe Storage".format(self.name)
                    )
                key = PBKDF2(my_pass, b"saltysalt", iterations=1).read(16)

            elif platform == utils.Platform.MAC:
                my_pass = keyring.get_password("Chrome Safe Storage", "Chrome").encode(
                    "utf8"
                )
                key = PBKDF2(my_pass, b"saltysalt", iterations=1003).read(16)

            if cookie["value"] or cookie["encrypted_value"][:3] not in [b"v11", b"v10"]:
                cookie["encrypted_value"] = cookie["value"]
            else:
                cookie["encrypted_value"] = cookie["encrypted_value"][3:]
                cipher = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, b" " * 16))
                decrypted = cipher.feed(
                    cookie["encrypted_value"][: int(len(cookie["encrypted_value"]) / 2)]
                )
                decrypted += cipher.feed(
                    cookie["encrypted_value"][int(len(cookie["encrypted_value"]) / 2) :]
                )
                decrypted += cipher.feed()
                cookie["encrypted_value"] = decrypted.decode("utf-8")
        else:
            cookie["encrypted_value"] = win32crypt.CryptUnprotectData(
                cookie["encrypted_value"], None, None, None, 0
            )[1].decode("utf-8")
        del cookie["value"]
        cookie["expiry"] = datetime.datetime.strptime(
            cookie["expiry"], "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=self._local_tz)
        return tuple(cookie.values())


class Chromium(Browser):
    """Chromium Browser

    Supported platforms (TODO: Mac OS support)

    * Linux
    * Windows

    Profile support: Yes
    """

    name = "Chromium"

    linux_path = ".config/chromium"
    windows_path = "AppData/Local/chromium/User Data"

    profile_support = True
    profile_dir_prefixes = Chrome.profile_dir_prefixes

    history_file = Chrome.history_file
    bookmarks_file = Chrome.bookmarks_file
    cookies_file = Chrome.cookies_file

    history_SQL = Chrome.history_SQL
    cookies_SQL = Chrome.cookies_SQL

    bookmarks_parser = Chrome.bookmarks_parser
    cookies_parser = Chrome.cookies_parser


class Firefox(Browser):
    """Mozilla Firefox Browser

    Supported platforms:

    * Windows
    * Linux
    * Mac OS

    Profile support: Yes
    """

    name = "Firefox"

    windows_path = "AppData/Roaming/Mozilla/Firefox/Profiles"
    linux_path = ".mozilla/firefox"
    mac_path = "Library/Application Support/Firefox/Profiles/"

    profile_support = True

    history_file = "places.sqlite"
    bookmarks_file = "places.sqlite"
    cookies_file = "cookies.sqlite"

    history_SQL = """
        SELECT
            datetime(
                visit_date/1000000, 'unixepoch', 'localtime'
            ) AS 'visit_time',
            url
        FROM
            moz_historyvisits
        INNER JOIN
            moz_places
        ON
            moz_historyvisits.place_id = moz_places.id
        WHERE
            visit_date IS NOT NULL AND url LIKE 'http%' AND title IS NOT NULL
    """

    cookies_SQL = """
        SELECT
            name, host, path, value, value, expiry, isSecure, isHttpOnly
        FROM
            moz_cookies
    """

    def bookmarks_parser(self, bookmark_path):
        """Returns bookmarks of a single profile for Firefox based browsers
        The returned datetimes are timezone-aware with the local timezone set
        by default

        :param bookmark_path : the path of the bookmark file
        :type bookmark_path : str
        :return a list of tuples of bookmark information
        :rtype: list(tuple(:py:class:`datetime.datetime`, str, str, str))
        """

        bookmarks_sql = """
            SELECT
                datetime(
                    moz_bookmarks.dateAdded/1000000,'unixepoch','localtime'
                ) AS added_time,
                url, moz_bookmarks.title, moz_folder.title
            FROM
                moz_bookmarks JOIN moz_places, moz_bookmarks as moz_folder
            ON
                moz_bookmarks.fk = moz_places.id
                AND moz_bookmarks.parent = moz_folder.id
            WHERE
                moz_bookmarks.dateAdded IS NOT NULL AND url LIKE 'http%'
                AND moz_bookmarks.title IS NOT NULL
        """
        conn = sqlite3.connect(f"file:{bookmark_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(bookmarks_sql)
        date_bookmarks = [
            (
                datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=self._local_tz
                ),
                url,
                title,
                folder,
            )
            for d, url, title, folder in cursor.fetchall()
        ]
        return date_bookmarks

    def cookies_parser(self, cookie):
        """Returns cookies of a single input for Chrome based browsers
        The returned datetimes are timezone-aware with the local timezone set
        by default

        :param cookie : dictionary containing cookie details
        :type cookie : dict
        :return a tuple of cookie information
        :rtype: list(tuple(:py:class: str, str, `datetime.datetime`, str, str, str))
        """
        cookie["expiry"] = datetime.datetime.utcfromtimestamp(
            cookie["expiry"]
        ).strftime("%Y-%m-%d %H:%M:%S")
        cookie["expiry"] = datetime.datetime.strptime(
            cookie["expiry"], "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=self._local_tz)
        del cookie["value"]
        return tuple(cookie.values())


class Safari(Browser):
    """Apple Safari browser

    Supported platforms:

    * Mac OS

    Profile support: No
    """

    name = "Safari"

    mac_path = "Library/Safari"

    profile_support = False

    history_file = "History.db"

    history_SQL = """
        SELECT
            datetime(
                visit_time + 978307200, 'unixepoch', 'localtime'
            ) as visit_time,
            url
        FROM
            history_visits
        INNER JOIN
            history_items
        ON
            history_items.id = history_visits.history_item
        ORDER BY
            visit_time DESC
    """


class Edge(Browser):
    """Microsoft Edge Browser

    Supported platforms

    * Windows
    * Mac OS

    Profile support: Yes
    """

    name = "Edge"

    windows_path = "AppData/Local/Microsoft/Edge/User Data"
    mac_path = "Library/Application Support/Microsoft Edge"

    profile_support = True
    profile_dir_prefixes = Chrome.profile_dir_prefixes

    history_file = Chrome.history_file
    bookmarks_file = Chrome.bookmarks_file
    cookies_file = Chrome.cookies_file

    history_SQL = Chrome.history_SQL
    cookies_SQL = Chrome.cookies_SQL

    bookmarks_parser = Chrome.bookmarks_parser
    cookies_parser = Chrome.cookies_parser


class Opera(Browser):
    """Opera Browser

    Supported platforms

    * Linux, Windows, Mac OS

    Profile support: No
    """

    name = "Opera"

    linux_path = ".config/opera"
    windows_path = "AppData/Roaming/Opera Software/Opera Stable"
    mac_path = "Library/Application Support/com.operasoftware.Opera"

    profile_support = False

    history_file = Chrome.history_file
    bookmarks_file = Chrome.bookmarks_file
    cookies_file = Chrome.cookies_file

    history_SQL = Chrome.history_SQL
    cookies_SQL = Chrome.cookies_SQL

    bookmarks_parser = Chrome.bookmarks_parser
    cookies_parser = Chrome.cookies_parser


class OperaGX(Browser):
    """Opera GX Browser

    Supported platforms

    * Windows

    Profile support: No
    """

    name = "OperaGX"

    windows_path = "AppData/Roaming/Opera Software/Opera GX Stable"

    profile_support = False

    history_file = Chrome.history_file
    bookmarks_file = Chrome.bookmarks_file

    history_SQL = Chrome.history_SQL
    cookies_SQL = Chrome.cookies_SQL

    bookmarks_parser = Chrome.bookmarks_parser
    cookies_parser = Chrome.cookies_parser


class Brave(Browser):
    """Brave Browser

    Supported platforms:

    * Linux
    * Mac OS

    Profile support: Yes
    """

    name = "Brave"

    linux_path = ".config/BraveSoftware/Brave-Browser"
    mac_path = "Library/Application Support/BraveSoftware/Brave-Browser"

    profile_support = True
    profile_dir_prefixes = Chrome.profile_dir_prefixes

    history_file = Chrome.history_file
    bookmarks_file = Chrome.bookmarks_file
    cookies_file = Chrome.cookies_file

    history_SQL = Chrome.history_SQL
    cookies_SQL = Chrome.cookies_SQL

    bookmarks_parser = Chrome.bookmarks_parser
    cookies_parser = Chrome.cookies_parser
