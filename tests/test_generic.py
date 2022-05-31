#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access
"""test for generic module."""
import os
import pathlib
from datetime import datetime
from unittest.mock import patch, Mock

import pytest
from browser_history import generic, utils
from browser_history.exceptions import BookmarksNotSupportedError
from browser_history.generic import ChromiumBasedBrowser
from browser_history.outputs import HistoryOutputs, BookmarksOutputs


def test_outputs_init():
    """test Outputs init"""
    obj = generic.HistoryOutputs()
    assert not obj.histories
    assert obj._format_map


@pytest.mark.parametrize(
    "entries, exp_res",
    [
        [[], "Timestamp,URL\r\n"],
        [
            [
                [datetime(2020, 1, 1), "https://google.com"],
                [datetime(2020, 1, 1), "https://example.com"],
            ],
            "Timestamp,URL\r\n"
            "2020-01-01 00:00:00,https://google.com\r\n"
            "2020-01-01 00:00:00,https://example.com\r\n",
        ],
    ],
)
def test_output_to_csv(entries, exp_res):
    """test Outputs.to_csv"""
    obj = generic.HistoryOutputs()
    obj.data.extend(entries)
    assert obj.to_csv() == exp_res


@pytest.mark.parametrize(
    "entries, exp_res",
    [
        [[], []],
        [
            [
                [datetime(2020, 1, 1), "https://google.com"],
                [datetime(2020, 1, 1), "https://google.com/imghp?hl=EN"],
                [datetime(2020, 1, 1), "https://example.com"],
            ],
            [
                (
                    "google.com",
                    [
                        [datetime(2020, 1, 1, 0, 0), "https://google.com"],
                        [
                            datetime(2020, 1, 1, 0, 0),
                            "https://google.com/imghp?hl=EN",
                        ],
                    ],
                ),
                (
                    "example.com",
                    [[datetime(2020, 1, 1, 0, 0), "https://example.com"]],
                ),
            ],
        ],
    ],
)
def test_output_sort_domain(entries, exp_res):
    """test Outputs.sort_domain"""
    obj = generic.HistoryOutputs()
    obj.data.extend(entries)
    assert list(obj.group_by_domain().items()) == exp_res


class _CustomBrowser(generic.Browser):
    name = "Custom browser"
    _history_file = ""
    _history_SQL = ""
    _linux_path = "random_path"
    profile_support = True


def test_browser_unknown_platform():
    with pytest.raises(NotImplementedError):
        _CustomBrowser(utils.Platform.OTHER)


def test_browser_profiles_remove_trailing_separator():
    browser = _CustomBrowser(utils.Platform.LINUX)
    browser._history_file = "history/"
    profile_filename = f"profile.file{os.sep}"
    mocked_os = Mock()
    mocked_os.walk.return_value = [
        [f"history/{profile_filename}", "dirname", [profile_filename]]
    ]
    mocked_os.path.split.return_value = [profile_filename]
    mocked_os.sep = os.sep
    with patch("browser_history.generic.os", mocked_os):
        trimmed_path = browser._profiles(profile_filename)[0]
    assert trimmed_path == f"{browser._history_file}{profile_filename}"[:-1]


def test_browser_bookmarks_paths_throws_error():
    browser = _CustomBrowser(utils.Platform.LINUX)
    with pytest.raises(BookmarksNotSupportedError):
        browser._bookmark_paths()


def test_browser_fetch_bookmarks_path_doesnt_exist():
    browser = _CustomBrowser(utils.Platform.LINUX)
    browser._bookmarks_file = "bookmarks.file"
    output = browser.fetch_bookmarks(["path/to/bookmarks"])
    assert output.bookmarks == []


def test_date_time_encoder_default_isoformat_only_date_type():
    initial_string = "date as string"
    entries = [(initial_string, "https://example.com")]
    outputs = HistoryOutputs()
    outputs.data.extend(entries)
    output_str = outputs.to_json(True)
    assert (
        output_str
        == f'{{"Timestamp": "{initial_string}", "URL": "https://example.com"}}'
    )


def test_outputs_save_invalid_output_format():
    outputs = HistoryOutputs()
    with pytest.raises(ValueError):
        outputs.save("file.name")


def test_chromium_based_browser_bookmark_parser_deep_hierarchy():
    class CustomChromiumBrowser(ChromiumBasedBrowser):
        name = "Test"
        _linux_path = "random_path"

    browser = CustomChromiumBrowser(utils.Platform.LINUX)
    nodes = {
        "roots": {
            "key": {
                "parent": {
                    "children": [
                        {
                            "type": "url",
                            "date_added": int(datetime.now().timestamp()),
                            "url": "foo.bar",
                            "name": "foo",
                        }
                    ]
                }
            }
        }
    }
    with patch("browser_history.generic.open"):
        with patch("browser_history.generic.json.load", Mock(return_value=nodes)):
            bookmark_list = browser._bookmarks_parser("/")
    assert len(bookmark_list) == 1
