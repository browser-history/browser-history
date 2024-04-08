"""This module defines all supported browsers and their functionality.

All browsers must inherit from :py:mod:`browser_history.generic.Browser`.
"""

import datetime
import sqlite3

from browser_history.generic import Browser, ChromiumBasedBrowser


class Chromium(ChromiumBasedBrowser):
    """Chromium Browser

    Supported platforms (TODO: Mac OS support)

    * Linux
    * Windows

    Profile support: Yes
    """

    name = "Chromium"
    aliases = ("chromiumhtm", "chromium-browser", "chromiumhtml")

    linux_path = ".config/chromium"
    windows_path = "AppData/Local/chromium/User Data"

    profile_support = True


class Chrome(ChromiumBasedBrowser):
    """Google Chrome Browser

    Supported platforms:

    * Windows
    * Linux
    * Mac OS

    Profile support: Yes
    """

    name = "Chrome"
    aliases = ("chromehtml", "google-chrome", "chromehtm")

    linux_path = ".config/google-chrome"
    windows_path = "AppData/Local/Google/Chrome/User Data"
    mac_path = "Library/Application Support/Google/Chrome/"

    profile_support = True


class Firefox(Browser):
    """Mozilla Firefox Browser

    Supported platforms:

    * Windows
    * Linux
    * Mac OS

    Profile support: Yes
    """

    name = "Firefox"
    aliases = ("firefoxurl",)

    linux_path = ".mozilla/firefox"
    windows_path = "AppData/Roaming/Mozilla/Firefox/Profiles"
    mac_path = "Library/Application Support/Firefox/Profiles/"

    profile_support = True

    history_file = "places.sqlite"
    bookmarks_file = "places.sqlite"

    history_SQL = """
        SELECT
            datetime(
                visit_date/1000000, 'unixepoch', 'localtime'
            ) AS 'visit_time',
            url,
            moz_places.title
        FROM
            moz_historyvisits
        INNER JOIN
            moz_places
        ON
            moz_historyvisits.place_id = moz_places.id
        WHERE
            visit_date IS NOT NULL AND url LIKE 'http%' AND title IS NOT NULL
    """

    def bookmarks_parser(self, bookmark_path):
        """Returns bookmarks of a single profile for Firefox based browsers
        The returned datetimes are timezone-aware with the local timezone set
        by default

        :param bookmark_path: the path of the bookmark file
        :type bookmark_path: str
        :return: a list of tuples of bookmark information
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
        conn.close()
        return date_bookmarks


class LibreWolf(Firefox):
    """LibreWolf Browser

    Supported platforms:

    * Linux


    Profile support: Yes
    """

    name = "LibreWolf"
    aliases = ("librewolfurl",)

    linux_path = ".librewolf"


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
            url,
            title
        FROM
            history_visits
        INNER JOIN
            history_items
        ON
            history_items.id = history_visits.history_item
        ORDER BY
            visit_time DESC
    """


class Edge(ChromiumBasedBrowser):
    """Microsoft Edge Browser

    Supported platforms

    * Windows
    * Mac OS

    Profile support: Yes
    """

    name = "Edge"
    aliases = ("msedgehtm", "msedge", "microsoft-edge", "microsoft-edge-dev")

    linux_path = ".config/microsoft-edge-dev"
    windows_path = "AppData/Local/Microsoft/Edge/User Data"
    mac_path = "Library/Application Support/Microsoft Edge"

    profile_support = True


class Opera(ChromiumBasedBrowser):
    """Opera Browser

    Supported platforms

    * Linux, Windows, Mac OS

    Profile support: No
    """

    name = "Opera"
    aliases = ("operastable", "opera-stable")

    linux_path = ".config/opera"
    windows_path = "AppData/Roaming/Opera Software/Opera Stable"
    mac_path = "Library/Application Support/com.operasoftware.Opera"

    profile_support = False


class OperaGX(ChromiumBasedBrowser):
    """Opera GX Browser

    Supported platforms

    * Windows

    Profile support: No
    """

    name = "OperaGX"
    aliases = ("operagxstable", "operagx-stable")

    windows_path = "AppData/Roaming/Opera Software/Opera GX Stable"

    profile_support = False


class Brave(ChromiumBasedBrowser):
    """Brave Browser

    Supported platforms:

    * Linux
    * Mac OS
    * Windows

    Profile support: Yes
    """

    name = "Brave"
    aliases = ("bravehtml",)

    linux_path = ".config/BraveSoftware/Brave-Browser"
    mac_path = "Library/Application Support/BraveSoftware/Brave-Browser"
    windows_path = "AppData/Local/BraveSoftware/Brave-Browser/User Data"

    profile_support = True


class Vivaldi(ChromiumBasedBrowser):
    """Vivaldi Browser

    Supported platforms (TODO: Add Mac OS support)

    * Linux
    * Windows

    Profile support: Yes
    """

    name = "Vivaldi"
    aliases = ("vivaldi-stable", "vivaldistable")

    linux_path = ".config/vivaldi"
    mac_path = "Library/Application Support/Vivaldi"
    windows_path = "AppData/Local/Vivaldi/User Data"

    profile_support = True


class Epic(ChromiumBasedBrowser):
    """Epic Privacy Browser

    Supported platforms (TODO: Add Mac OS support)

    * Windows
    * Mac OS

    Profile support: No
    """

    name = "Epic Privacy Browser"

    windows_path = "AppData/Local/Epic Privacy Browser/User Data/Default"
    mac_path = "Library/Application Support/HiddenReflex/Epic/Default"

    profile_support = False
