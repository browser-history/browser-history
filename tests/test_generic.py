#!/usr/bin/env python
# -*- coding: utf-8 -*-
from browser_history import generic


def test_outputs_init():
    obj = generic.Outputs()
    assert not obj.entries
