"""This module defines all supported browsers and their functionality.

All browsers must inherit from :py:mod:`browser_history.generic.Browser`.
"""
import sqlite3
import json
import datetime
import os
from browser_history.generic import Browser

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

    history_SQL = """SELECT
            datetime(visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime') as 'visit_time',
        urls.url from urls,visits
        WHERE urls.id = visits.url ORDER BY visit_time DESC"""

    def bookmarks_parser(self,bookmark_path):
        """Returns bookmarks of a single profile for Chrome based browsers
        The returned datetimes are timezone-aware with the local timezone set by default

        :param bookmark_path : the path of the bookmark file
        :type bookmark_path : str
        :return a list of tuples of bookmark information
        :rtype: list(tuple(:py:class:`datetime.datetime`, str, str, str))
        """

        def _deeper(array,folder,bookmarks_list):
            for node in array:
                if node['type'] == 'url':
                    d_t =datetime.datetime(1601, 1, 1) + \
                        datetime.timedelta(microseconds=int(node['date_added']))
                    bookmarks_list.append((
                        d_t.replace(
                                    microsecond =0 ,tzinfo=self._local_tz
                                ),
                        node['url'],
                        node['name'],
                        folder,
                    ))
                else:
                    bookmarks_list = _deeper(node['children'],
                                            folder+os.sep+node['name'],
                                            bookmarks_list)
            return bookmarks_list

        with open(bookmark_path) as b_p:
            b_m = json.load(b_p)
            bookmarks_list = []
            for root in b_m['roots']:
                bookmarks_list = _deeper(b_m['roots'][root]['children'],root, bookmarks_list)
        return bookmarks_list

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

    history_SQL = Chrome.history_SQL


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

    history_SQL = """SELECT
            datetime(visit_date/1000000, 'unixepoch', 'localtime') AS 'visit_time',
            url
        FROM moz_historyvisits INNER JOIN moz_places ON moz_historyvisits.place_id = moz_places.id 
        WHERE visit_date IS NOT NULL AND url LIKE 'http%' AND title IS NOT NULL"""

    def bookmarks_parser(self,bookmark_path):
        """Returns bookmarks of a single profile for Firefox based browsers
        The returned datetimes are timezone-aware with the local timezone set by default

        :param bookmark_path : the path of the bookmark file
        :type bookmark_path : str
        :return a list of tuples of bookmark information
        :rtype: list(tuple(:py:class:`datetime.datetime`, str, str, str))
        """

        bookmarks_sql = """SELECT
            datetime(moz_bookmarks.dateAdded/1000000,'unixepoch','localtime') 
            AS added_time,url,moz_bookmarks.title ,moz_folder.title
            FROM moz_bookmarks INNER JOIN moz_places,moz_bookmarks as moz_folder 
            ON moz_bookmarks.fk = moz_places.id AND moz_bookmarks.parent = moz_folder.id
            WHERE moz_bookmarks.dateAdded IS NOT NULL AND url LIKE 'http%' 
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
                            for d, url ,title ,folder in cursor.fetchall()
                        ]
        return date_bookmarks

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

    history_SQL = """SELECT
        datetime(visit_time + 978307200, 'unixepoch', 'localtime') as visit_time, url
        FROM
            history_visits
        INNER JOIN
        history_items ON
            history_items.id = history_visits.history_item
        ORDER BY
            visit_time DESC"""


class Edge(Browser):
    """Microsoft Edge Browser

    Supported platforms (TODO: Mac OS support)

    * Windows

    Profile support: Yes
    """

    name = "Edge"

    windows_path = "AppData/Local/Microsoft/Edge/User Data"

    profile_support = True
    profile_dir_prefixes = Chrome.profile_dir_prefixes

    history_file = Chrome.history_file
    bookmarks_file = Chrome.bookmarks_file

    history_SQL = Chrome.history_SQL

    bookmarks_parser = Chrome.bookmarks_parser

class Opera(Browser):
    """Opera Browser

    Supported platforms (TODO: Mac OS support)

    * Linux, Windows

    Profile support: No
    """
    name = "Opera"

    linux_path = ".config/opera"
    windows_path = "AppData/Roaming/Opera Software/Opera Stable"

    profile_support = False

    history_file = Chrome.history_file
    bookmarks_file = Chrome.bookmarks_file

    history_SQL = Chrome.history_SQL

    bookmarks_parser = Chrome.bookmarks_parser

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

    bookmarks_parser = Chrome.bookmarks_parser

class Brave(Browser):
    """Brave Browser

    Supported platforms:

    * Linux

    Profile support: Yes
    """

    name = "Brave"

    linux_path = ".config/BraveSoftware/Brave-Browser"

    profile_support = True
    profile_dir_prefixes = Chrome.profile_dir_prefixes

    history_file = Chrome.history_file
    bookmarks_file = Chrome.bookmarks_file

    history_SQL = Chrome.history_SQL

    bookmarks_parser = Chrome.bookmarks_parser
