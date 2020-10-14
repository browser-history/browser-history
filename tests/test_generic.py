#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access
"""test for generic module."""
from datetime import datetime

import pytest

from browser_history import generic


def test_outputs_init():
    """test Outputs init"""
    obj = generic.Outputs()
    assert not obj.entries
    assert obj._format_map

@pytest.mark.parametrize(
    'entries, exp_res', [
        [[], 'Timestamp,URL\r\n'],
        [
            [
                [datetime(2020, 1, 1), 'https://google.com'],
                [datetime(2020, 1, 1), 'https://example.com'],
            ], 'Timestamp,URL\r\n'
            '2020-01-01 00:00:00,https://google.com\r\n'
            '2020-01-01 00:00:00,https://example.com\r\n'
],
    ]
)
def test_output_to_csv(entries, exp_res):
    """test Outputs.to_csv"""
    obj = generic.Outputs()
    obj.entries = entries
    assert obj.to_csv() == exp_res


@pytest.mark.parametrize(
    'entries, exp_res', [
        [[], []],
        [[
            [datetime(2020, 1, 1), 'https://google.com'],
            [datetime(2020, 1, 1), 'https://google.com/imghp?hl=EN'],
            [datetime(2020, 1, 1), 'https://example.com'],
        ],
        [
            ('google.com', [
                [datetime(2020, 1, 1, 0, 0), 'https://google.com'],
                [datetime(2020, 1, 1, 0, 0), 'https://google.com/imghp?hl=EN']]),
            ('example.com', [[datetime(2020, 1, 1, 0, 0), 'https://example.com']])
        ]
]
    ]
)
def test_output_sort_domain(entries, exp_res):
    """test Outputs.sort_domain"""
    obj = generic.Outputs()
    obj.entries = entries
    assert list(obj.sort_domain().items()) == exp_res
