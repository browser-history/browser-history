from datetime import datetime

from pytest import MonkeyPatch

from browser_history.browsers import Safari
from browser_history.generic import Outputs

from .utils import (  # noqa: F401; pylint: disable=unused-import
    become_mac,
    change_homedir,
)

# pylint: disable=redefined-outer-name,unused-argument


def test_none_titles(
    become_mac, change_homedir, monkeypatch: MonkeyPatch  # noqa: F811
):
    # see https://github.com/browser-history/browser-history/issues/272
    # and https://github.com/browser-history/browser-history/pull/273

    outputs = Outputs("history")
    same_time = datetime.now().astimezone()
    outputs.histories = [
        (same_time, "same_url", "Title"),
        (same_time, "same_url", None),
    ]

    monkeypatch.setattr(Safari, "fetch_history", lambda *args: outputs)

    from browser_history import get_history

    outputs = get_history()
