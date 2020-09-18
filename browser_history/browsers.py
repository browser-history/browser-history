"""This module defines all supported browsers and their functionality.

All browsers must inherit from :py:mod:`browser_history.generic.Browser`.
"""
from browser_history.generic import Browser

class Chrome(Browser):
    """Google Chrome Browser

    Supported platforms:

    * Windows
    * Linux
    * Mac OS

    Profile support: Yes
    """
    name = 'Chrome'

    windows_path = 'AppData\\Local\\Google\\Chrome\\User Data'
    mac_path = 'Library/Application Support/Google/Chrome/'
    linux_path = '.config/google-chrome'

    profile_support = True
    profile_dir_prefixes = ['Default*', 'Profile*']

    history_file = 'History'

    history_SQL = """SELECT
            datetime(visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime') as 'visit_time',
        urls.url from urls,visits
        WHERE urls.id = visits.url ORDER BY visit_time DESC"""

class Chromium(Browser):
    """Chromium Browser

    Supported platforms (TODO: Windows and Mac OS support)

    * Linux

    Profile support: Yes
    """
    name = "Chromium"

    linux_path = '.config/chromium'

    profile_support = True
    profile_dir_prefixes = Chrome.profile_dir_prefixes

    history_file = Chrome.history_file

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

    windows_path = 'AppData\\Roaming\\Mozilla\\Firefox\\Profiles'
    linux_path = '.mozilla/firefox'
    mac_path = 'Library/Application Support/Firefox/Profiles/'

    profile_support = True

    history_file = "places.sqlite"
    history_SQL = """SELECT
            datetime(last_visit_date/1000000, 'unixepoch', 'localtime') AS 'visit_time',
            url
        FROM moz_historyvisits NATURAL JOIN moz_places WHERE
        last_visit_date IS NOT NULL AND url LIKE 'http%' AND title IS NOT NULL"""

class Safari(Browser):
    """Apple Safari browser

    Supported platforms:

    * Mac OS

    Profile support: No
    """
    name = "Safari"

    mac_path = 'Library/Safari'

    profile_support = False

    history_file = 'History.db'
    history_SQL = """SELECT
        datetime(visit_time + 978307200, 'unixepoch', 'localtime') as visit_time, url
        FROM
            history_visits
        INNER JOIN
        history_items ON
            history_items.id = history_visits.history_item
        ORDER BY
            visit_time DESC"""
